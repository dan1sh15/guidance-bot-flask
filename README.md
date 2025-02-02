# GuidanceBot - AI-powered Career Counseling & Emotional Support Platform (Flask Version)

GuidanceBot is an AI-powered career counseling and emotional support platform that helps individuals make informed career decisions and provides emotional support. It offers personalized career guidance through AI-driven insights, job recommendations, and wellness support. This repository contains the backend of the platform built using Flask.

## Features
- **Job Role Data**: Provides a list of job roles and their relevant projects and skills.
- **Course Recommendations**: Recommends Coursera and Udemy courses based on the selected job role.
- **Career Path Guidance**: Offers career progression steps for different job roles, including experience requirements and next career steps.
- **Required Projects and Skills**: Offers list of projects and skills required for the particular job role.

## Tech Stack
- **Backend**: Flask
- **Data Handling**: Pandas
- **Text Matching**: FuzzyWuzzy for fuzzy matching job role keywords
- **Dataset**: CSV files (Profiles, Coursera courses, Udemy courses, Career paths)
- **CORS**: Flask-CORS for enabling cross-origin requests

## Project Setup

### Prerequisites
Make sure you have the following installed on your machine:
- Python (>= 3.6)
- pip (for installing dependencies)

### Setup Instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/dan1sh15/guidance-bot-flask
