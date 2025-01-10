# McGill Registrator

## Overview
This Python script automates checking course availability and registering for a course on the McGill Horizon system using Selenium.

## Prerequisites
1. **Python**
2. **Google Chrome** and compatible **ChromeDriver**
3. Install Selenium:
   ```bash
   pip install selenium
   ```

## Setup
1. Replace `username` and `password` with your McGill credentials.
2. Update these variables in the script:
- `term`: Term code (e.g., `202505` for Winter 2025).
- `subject`: Subject code (e.g., `PHYS`).
- `course_number`: Course number (e.g., `183`).
- `type`: Class type (e.g., `Lecture`).
- `student_id`: Your McGill username.
- `password`: Your McGill password.

## Usage
1. Run the script:
   ```bash
   python script.py
   ```
2. The script continuously checks availability every 20 seconds.
3. Registers automatically if a seat is available.
