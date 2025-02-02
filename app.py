import os
from flask import Flask, jsonify
import pandas as pd
from fuzzywuzzy import process

app = Flask(__name__)

# Load your datasets
df = pd.read_csv('profiles_dataset.csv')
course_df = pd.read_csv('Coursera.csv')
udemy_df = pd.read_csv('Udemy.csv')
career_df = pd.read_csv('career_paths.csv')

# Job role keywords mapping (same as before)
job_role_keywords = {
    # Define your job role and keyword mappings here...
}


@app.route("/job-roles", methods=["GET"])
def get_job_roles():
    unique_roles = df["Job Role"].dropna().unique()
    return jsonify({"job_roles": unique_roles.tolist()})


@app.route("/projects-and-skills/<job_role>", methods=["GET"])
def get_projects_and_skills(job_role):
    filtered_df = df[(df["Job Role"] == job_role) & (df["Experience"] > 10)]
    projects = filtered_df["Projects"].dropna().sample(min(10, len(filtered_df)), random_state=42).tolist()

    # Extract unique skills
    all_skills = set()
    for skills in df["Skills"].dropna():
        skill_list = [skill.strip() for skill in skills.split(",")]
        all_skills.update(skill_list)

    return jsonify({"projects": projects, "skills": sorted(all_skills)})


@app.route("/recommended-courses/<job_role>", methods=["GET"])
def get_recommended_courses(job_role):
    keywords = job_role_keywords.get(job_role, [])
    matched_courses = find_relevant_courses(course_df, keywords)
    filtered_courses = course_df[course_df["course"].isin(matched_courses)].sort_values(by="rating", ascending=False)
    result = filtered_courses[["course", "partner", "skills", "duration", "crediteligibility", "rating"]].to_dict(
        orient="records")
    return jsonify(result)


@app.route("/recommended-udemy-courses/<job_role>", methods=["GET"])
def get_recommended_udemy_courses(job_role):
    keywords = job_role_keywords.get(job_role, [])
    matched_courses = udemy_df[udemy_df["title"].str.contains(job_role, case=False, na=False, regex=True)]
    for keyword in keywords:
        matched_courses = pd.concat(
            [matched_courses, udemy_df[udemy_df["title"].str.contains(keyword, case=False, na=False, regex=True)]])
    matched_courses = matched_courses.drop_duplicates().sample(10, random_state=42)
    result = matched_courses[["title", "description", "instructor", "duration"]].to_dict(orient="records")
    return jsonify(result)


@app.route("/career-path/<job_role>", methods=["GET"])
def get_career_path(job_role):
    career_progression = career_df[career_df["job role"].str.contains(job_role, case=False, na=False, regex=True)]
    result = career_progression[["job role", "experience", "next career step"]].to_dict(orient="records")
    return jsonify(result)


def find_relevant_courses(course_df, keywords):
    matched_courses = []
    for course in course_df["course"].dropna().unique():
        best_match, score = process.extractOne(course, keywords)
        if score > 90:
            matched_courses.append(course)
    return matched_courses


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use environment variable PORT if available, else default to 5000
    app.run(host="0.0.0.0", port=port, debug=True)
