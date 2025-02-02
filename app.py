import os
from flask import Flask, jsonify
from flask_cors import CORS  # Import CORS
import pandas as pd
from fuzzywuzzy import process

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load your datasets
df = pd.read_csv('profiles_dataset.csv')
course_df = pd.read_csv('Coursera.csv')
udemy_df = pd.read_csv('Udemy.csv')
career_df = pd.read_csv('career_paths.csv')

# Convert "Experience" column to numeric to avoid TypeError
df["Experience"] = pd.to_numeric(df["Experience"].astype(str).str.extract(r'(\d+)')[0], errors='coerce').astype('Int64')
career_df.columns = career_df.columns.str.strip().str.lower()
# Job role keywords mapping (Define this based on your dataset)
job_role_keywords = {
    "HR Manager": ["Human Resources", "HR Management", "Talent Acquisition"],
    "Marketing Specialist": ["Marketing", "Digital Marketing", "Brand Management"],
    "Financial Analyst": ["Finance", "Financial Modeling", "Investment Analysis"],
    "Content Writer": ["Content Writing", "Creative Writing", "Copywriting"],
    "SEO Specialist": ["SEO", "Search Engine Optimization", "Digital Marketing"],
    "DevOps Engineer": ["DevOps", "Cloud Infrastructure", "CI/CD"],
    "Product Manager": ["Product Management", "Business Strategy"],
    "Network Engineer": ["Networking", "Cybersecurity", "Network Administration"],
    "Graphic Designer": ["Graphic Design", "Adobe Photoshop", "Illustration"],
    "Software Engineer": ["Software Development", "System Design", "Web Development"],
    "Data Scientist": ["Data Science", "Machine Learning"],
    "UX Designer": ["User Experience", "UX Design", "Human-Centered Design"]
}

@app.route("/job-roles", methods=["GET"])
def get_job_roles():
    unique_roles = df["Job Role"].dropna().unique()
    return jsonify({"job_roles": unique_roles.tolist()})


@app.route("/projects-and-skills/<job_role>", methods=["GET"])
def get_projects_and_skills(job_role):
    """Returns projects and skills for a given job role"""

    # Ensure the job_role exists in dataset
    if job_role not in df["Job Role"].unique():
        return jsonify({"error": "Job role not found"}), 404

    # Filter the dataset based on job role (no experience condition)
    filtered_df = df[df["Job Role"] == job_role]

    if filtered_df.empty:
        return jsonify({"message": "No candidates found for this role"}), 404

    # Select projects (max 10)
    projects = filtered_df["Projects"].dropna().sample(min(10, len(filtered_df)), random_state=42).tolist()

    # Extract unique skills
    all_skills = set()
    for skills in filtered_df["Skills"].dropna():  # Use filtered_df to get relevant skills
        skill_list = [skill.strip() for skill in skills.split(",")]
        all_skills.update(skill_list)

    return jsonify({"projects": projects, "skills": sorted(all_skills)})



@app.route("/recommended-courses/<job_role>", methods=["GET"])
def get_recommended_courses(job_role):
    keywords = job_role_keywords.get(job_role, [])
    matched_courses = find_relevant_courses(course_df, keywords)

    # Ensure there are matched courses
    if not matched_courses:
        return jsonify({"message": "No relevant courses found"}), 404

    # Filter and sort by rating (descending)
    filtered_courses = course_df[course_df["course"].isin(matched_courses)].sort_values(by="rating", ascending=False)

    # Drop rows with any NaN values in relevant columns
    filtered_courses = filtered_courses.dropna(subset=["course", "partner", "skills", "duration", "crediteligibility", "rating"])

    # Limit to maximum 10 results
    result = filtered_courses.head(10)[["course", "partner", "skills", "duration", "crediteligibility", "rating"]].to_dict(orient="records")

    return jsonify(result)

@app.route("/recommended-udemy-courses/<job_role>", methods=["GET"])
def get_recommended_udemy_courses(job_role):
    keywords = job_role_keywords.get(job_role, [])

    if not keywords:
        return jsonify({"message": "No relevant Udemy courses found"}), 404

    # Filter Udemy courses
    matched_courses = udemy_df[udemy_df["title"].str.contains(job_role, case=False, na=False, regex=True)]

    for keyword in keywords:
        matched_courses = pd.concat(
            [matched_courses, udemy_df[udemy_df["title"].str.contains(keyword, case=False, na=False, regex=True)]])

    matched_courses = matched_courses.drop_duplicates().sample(min(10, len(matched_courses)), random_state=42)

    if matched_courses.empty:
        return jsonify({"message": "No relevant Udemy courses found"}), 404

    result = matched_courses[["title", "description", "instructor", "duration"]].to_dict(orient="records")
    return jsonify(result)


@app.route("/career-path/<job_role>", methods=["GET"])
def get_career_path(job_role):
    # Filter data for the selected job role
    career_progression = career_df[career_df["job role"].str.contains(job_role, case=False, na=False, regex=True)]

    if career_progression.empty:
        return jsonify({"message": f"No career path data found for '{job_role}'."}), 404

    # Extract next career step details
    result = []
    for _, row in career_progression.iterrows():
        career_step = {
            "current_role": row["job role"],
            "experience_required": row["experience"],
            "next_step": row["next career step"],
            "salary": row.get("salary", "N/A")
        }

        # Check if there is a next-to-next career step
        # next_step_data = career_df[
        #     career_df["job role"].str.contains(row["next career step"], case=False, na=False, regex=True)]
        # if not next_step_data.empty:
        #     next_to_next = next_step_data.iloc[0]
        #     career_step["next_to_next"] = {
        #         "role": next_to_next["next career step"],
        #         "experience_required": next_to_next["experience"],
        #         "salary": next_to_next.get("avg salary", "N/A")
        #     }

        result.append(career_step)

    return jsonify(result)


def find_relevant_courses(course_df, keywords):
    if not keywords:
        return []

    matched_courses = []
    for course in course_df["course"].dropna().unique():
        best_match, score = process.extractOne(course, keywords)
        if score > 80:  # Lowered threshold to 80 for more matches
            matched_courses.append(course)

    return matched_courses

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use PORT from env, default to 5000
    app.run(host="0.0.0.0", port=port, debug=True)
