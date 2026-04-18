# NT Fauna Recordings

## Project Overview

This project is a web-based application developed for the theme **“Listening to NT’s Disappearing Animals”**. The system allows users to explore endangered species in the Northern Territory, record observations using audio evidence, and report anomalies in submitted data.

The goal of the project is to simulate a simple environmental monitoring platform where real-world data can be collected and validated through user interaction.

---

## Key Features

- View threatened species (CR, EN, VU categories)
- Record observations with:
  - Audio upload
  - Location
  - Confidence score
- Report anomalies on suspicious observations
- Admin interface for managing data

---

## External Dataset

The species data used in this project comes from the Northern Territory Government open data portal:

https://data.nt.gov.au/dataset/nt-fauna-species-checklist

### Dataset Usage

The original dataset contains a wide range of fauna records. However, not all of them were relevant to this project.

### Data Cleaning Process

The dataset was cleaned before being used in the application. The cleaning process involved:

- Filtering only **threatened species** (CR, EN, VU)
- Removing unnecessary columns
- Standardising column names to match the Django model fields
- Handling missing or inconsistent values (e.g. replacing "N/A" with null)
- Exporting the cleaned data into a new Excel file

The cleaned dataset is stored in: dataset/nt_species_threatened_cleaned.xlsx


## Setup Instructions

### 1. Clone the repository
- git clone https://github.com/lance5828/HIT237-Group4.git

### 2. Create virtual environment
- python -m venv venv (Inside nt_fauna_recordings)

### 3. Install dependencies
- pip install -r requirements.txt (from the root folder)

### 4. Run the import command
- python manage.py import_species ../dataset/nt_species_threatened_cleaned.xlsx

### 4. Apply migrations
- python manage.py migrate

### 5. Create a superuser
- python manage.py createsuperuser




