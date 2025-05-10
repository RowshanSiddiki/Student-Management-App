import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px


def get_connection():
    """Establishes a database connection."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='123456Akib',
            database='Student_records'
        )
        return connection
    except mysql.connector.Error as err:
        st.error(f"Error connecting to database: {err}")
        return None

def get_departments():
    """Retrieves departments from the database."""
    connection = get_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT dept_id, dept_name FROM departments")
        departments = cursor.fetchall()
        cursor.close()
        connection.close()
        return departments
    return []

def add_student(student_id, name, dept_id, subjects, scores):
    """Adds a student and their performance to the database."""
    connection = get_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute(
                "INSERT INTO students (student_id, name, dept_id) VALUES (%s, %s, %s)",
                (student_id, name, dept_id),
            )
            connection.commit()

            # Add subjects and scores
            for subject, score in zip(subjects, scores):
                cursor.execute(
                    "INSERT INTO performance (student_id, subject, score) VALUES (%s, %s, %s)",
                    (student_id, subject, score),
                )
            connection.commit()

            st.success("Student and performance added successfully!")
        except mysql.connector.Error as err:
            st.error(f"Error adding student: {err}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

def get_student_performance():
    """Retrieves student performance data with department names."""
    connection = get_connection()
    if connection:
        query = """
        SELECT s.student_id, s.name, d.dept_name, p.subject, p.score
        FROM students s
        JOIN departments d ON s.dept_id = d.dept_id
        LEFT JOIN performance p ON s.student_id = p.student_id
        """
        df = pd.read_sql(query, connection)
        connection.close()
        return df
    return pd.DataFrame() #Return empty dataframe if connection fails.

def main():
    st.write("<h1 style='text-align: center; color: skyblue;'>📜 Student Management App</h1>", unsafe_allow_html=True)

    # Add Student Section
    st.header("Add Student")
    student_id = st.number_input("Student ID", min_value=1)
    name = st.text_input("Name")
    departments = get_departments()
    dept_options = {dept[1]: dept[0] for dept in departments}
    dept_name = st.selectbox("Department", list(dept_options.keys()))

    # Add subjects and scores input
    subjects = []
    scores = []
    subject = st.text_input("Subject")
    score = st.number_input("Score", min_value=0, max_value=100, value=50)

    if st.button("Add Student"):
        if name and dept_name and subject and score:
            subjects.append(subject)
            scores.append(score)
            add_student(student_id, name, dept_options[dept_name], subjects, scores)
        else:
            st.warning("Please fill in all fields.")

    # Student Performance Analysis
    st.header("Student Performance Analysis")
    df = get_student_performance()
    if not df.empty:
        st.dataframe(df)
        st.subheader("Analysis:")
        st.write(f"Total students: {df['student_id'].nunique()}")

        if 'score' in df.columns: #Check if the score column exists before doing any calculations.
            average_score = df['score'].mean()
            st.write(f"Average score: {average_score:.2f}")

            # Example: Display average score per department
            st.subheader("Average Score per Department")
            avg_dept_score = df.groupby('dept_name')['score'].mean().dropna()
            st.dataframe(avg_dept_score)

            # Plot for subjects with scores
            st.subheader("Subject Scores")
            subject_scores = df.groupby('subject')['score'].mean().dropna().reset_index()
            if not subject_scores.empty:
                fig1 = px.bar(subject_scores, x='subject', y='score', title='📊 Bar Chart', height=400, width=800)
                fig2 = px.line(subject_scores, x='subject', y='score', title='📉 Line Chart', height=400, width=800)

                col1, col2 = st.columns(2)
                with col1:
                    st.plotly_chart(fig1)
                with col2:
                    st.plotly_chart(fig2)
            else:
                st.write("No subject score data available.")
    else:
        st.write("No student performance data available.")

if __name__ == "__main__":
    main()
    st.markdown("<div style='margin-top: 100px;'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: skyblue;'>🧤 Developed By</h3>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: center; color: skyblue;'>Rowshan Siddiki | Arnika Islam | Ayman Ishraq</h5>", unsafe_allow_html=True)