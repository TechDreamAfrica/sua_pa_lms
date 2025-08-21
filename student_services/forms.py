from django import forms
from django.contrib.auth.models import User
from .models import AcademicRecord
from lms.models import Course
import csv
from io import TextIOWrapper

class AcademicRecordForm(forms.ModelForm):
    """Form for single academic record entry"""
    
    class Meta:
        model = AcademicRecord
        fields = ['student', 'course', 'semester', 'academic_year', 'grade', 'grade_points', 'credits_earned']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'course': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'semester': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'academic_year': forms.TextInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm',
                'placeholder': 'e.g., 2024-2025'
            }),
            'grade': forms.Select(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
            }),
            'grade_points': forms.NumberInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm',
                'step': '0.01',
                'min': '0',
                'max': '4.0'
            }),
            'credits_earned': forms.NumberInput(attrs={
                'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm',
                'min': '0'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter students to only show students
        self.fields['student'].queryset = User.objects.filter(
            userprofile__user_type='student'
        ).order_by('first_name', 'last_name')
        
        # Set semester choices
        self.fields['semester'].widget = forms.Select(
            choices=[
                ('', 'Select Semester'),
                ('fall', 'Fall'),
                ('spring', 'Spring'),
                ('summer', 'Summer'),
                ('winter', 'Winter'),
            ],
            attrs=self.fields['semester'].widget.attrs
        )
        
        # Set grade choices
        self.fields['grade'].widget = forms.Select(
            choices=[
                ('', 'Select Grade'),
                ('A+', 'A+ (4.0)'),
                ('A', 'A (3.7)'),
                ('A-', 'A- (3.3)'),
                ('B+', 'B+ (3.0)'),
                ('B', 'B (2.7)'),
                ('B-', 'B- (2.3)'),
                ('C+', 'C+ (2.0)'),
                ('C', 'C (1.7)'),
                ('C-', 'C- (1.3)'),
                ('D+', 'D+ (1.0)'),
                ('D', 'D (0.7)'),
                ('F', 'F (0.0)'),
                ('IC', 'Incomplete'),
                ('W', 'Withdrawn'),
                ('P', 'Pass'),
                ('NP', 'No Pass'),
            ],
            attrs=self.fields['grade'].widget.attrs
        )

class BulkAcademicRecordUploadForm(forms.Form):
    """Form for bulk CSV upload of academic records"""
    
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
        }),
        help_text="Select the course for which you're uploading grades"
    )
    
    semester = forms.ChoiceField(
        choices=[
            ('', 'Select Semester'),
            ('fall', 'Fall'),
            ('spring', 'Spring'),
            ('summer', 'Summer'),
            ('winter', 'Winter'),
        ],
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm'
        })
    )
    
    academic_year = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-uct-blue focus:ring-uct-blue sm:text-sm',
            'placeholder': 'e.g., 2024-2025'
        })
    )
    
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-uct-blue file:text-white hover:file:bg-blue-700',
            'accept': '.csv'
        }),
        help_text="Upload a CSV file with columns: student_id, grade, grade_points, credits_earned"
    )
    
    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            raise forms.ValidationError('File must be a CSV file.')
        
        # Check file size (limit to 5MB)
        if csv_file.size > 5 * 1024 * 1024:
            raise forms.ValidationError('File size must be less than 5MB.')
        
        return csv_file
    
    def process_csv(self, course, semester, academic_year):
        """Process the CSV file and return a list of records to create"""
        csv_file = self.cleaned_data['csv_file']
        records_to_create = []
        errors = []
        
        try:
            # Read CSV file
            file_data = TextIOWrapper(csv_file.file, encoding='utf-8')
            csv_reader = csv.DictReader(file_data)
            
            # Validate CSV headers
            required_headers = ['student_id', 'grade', 'grade_points', 'credits_earned']
            if not all(header in csv_reader.fieldnames for header in required_headers):
                raise forms.ValidationError(
                    f"CSV must contain columns: {', '.join(required_headers)}"
                )
            
            row_number = 1
            for row in csv_reader:
                row_number += 1
                
                try:
                    # Get student by student_id or username
                    student_id = row['student_id'].strip()
                    try:
                        # Try to find by student_id first
                        student = User.objects.get(userprofile__student_id=student_id)
                    except User.DoesNotExist:
                        # If not found, try by username
                        try:
                            student = User.objects.get(username=student_id)
                        except User.DoesNotExist:
                            errors.append(f"Row {row_number}: Student '{student_id}' not found")
                            continue
                    
                    # Validate student is actually a student
                    if not hasattr(student, 'userprofile') or student.userprofile.user_type != 'student':
                        errors.append(f"Row {row_number}: User '{student_id}' is not a student")
                        continue
                    
                    # Check if record already exists
                    if AcademicRecord.objects.filter(
                        student=student,
                        course=course,
                        semester=semester,
                        academic_year=academic_year
                    ).exists():
                        errors.append(f"Row {row_number}: Academic record already exists for student '{student_id}'")
                        continue
                    
                    # Validate grade points
                    try:
                        grade_points = float(row['grade_points'])
                        if grade_points < 0 or grade_points > 4.0:
                            errors.append(f"Row {row_number}: Grade points must be between 0.0 and 4.0")
                            continue
                    except ValueError:
                        errors.append(f"Row {row_number}: Invalid grade points '{row['grade_points']}'")
                        continue
                    
                    # Validate credits
                    try:
                        credits_earned = int(row['credits_earned'])
                        if credits_earned < 0:
                            errors.append(f"Row {row_number}: Credits earned must be non-negative")
                            continue
                    except ValueError:
                        errors.append(f"Row {row_number}: Invalid credits earned '{row['credits_earned']}'")
                        continue
                    
                    # Create record object (don't save yet)
                    record = AcademicRecord(
                        student=student,
                        course=course,
                        semester=semester,
                        academic_year=academic_year,
                        grade=row['grade'].strip().upper(),
                        grade_points=grade_points,
                        credits_earned=credits_earned
                    )
                    
                    records_to_create.append(record)
                    
                except Exception as e:
                    errors.append(f"Row {row_number}: {str(e)}")
            
        except UnicodeDecodeError:
            raise forms.ValidationError("File encoding error. Please ensure the CSV file is UTF-8 encoded.")
        except Exception as e:
            raise forms.ValidationError(f"Error processing CSV file: {str(e)}")
        
        if errors:
            raise forms.ValidationError("CSV processing errors:\n" + "\n".join(errors))
        
        return records_to_create
