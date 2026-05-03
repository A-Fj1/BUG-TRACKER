from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), "bugtracker.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    def lower_row(cursor, row):
        return {col[0].lower(): val for col, val in zip(cursor.description, row)}
    conn.row_factory = lower_row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS User_Table (
            User_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT, Email TEXT, Role TEXT
        );
        CREATE TABLE IF NOT EXISTS Team (
            Team_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Team_Name TEXT
        );
        CREATE TABLE IF NOT EXISTS Project (
            Project_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Project_Name TEXT, Description TEXT,
            Start_Date TEXT, End_Date TEXT, Project_Status TEXT,
            Team_ID INTEGER, FOREIGN KEY (Team_ID) REFERENCES Team(Team_ID)
        );
        CREATE TABLE IF NOT EXISTS Issue (
            Issue_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Title TEXT, Description TEXT, Priority TEXT,
            Issue_Type TEXT, Status TEXT, Due_Date TEXT,
            Project_ID INTEGER, User_ID INTEGER,
            FOREIGN KEY (Project_ID) REFERENCES Project(Project_ID),
            FOREIGN KEY (User_ID) REFERENCES User_Table(User_ID)
        );
        CREATE TABLE IF NOT EXISTS Comment_Table (
            Comment_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Content TEXT, Date_Posted TEXT,
            User_ID INTEGER, Issue_ID INTEGER,
            FOREIGN KEY (User_ID) REFERENCES User_Table(User_ID),
            FOREIGN KEY (Issue_ID) REFERENCES Issue(Issue_ID)
        );
        """)
        cur = conn.execute("SELECT COUNT(*) FROM User_Table").fetchone()
        count = list(cur.values())[0] if isinstance(cur, dict) else cur[0]
        if count == 0:
            conn.executescript("""
            INSERT INTO User_Table VALUES (1,'Ahmed','ahmed@email.com','Developer');
            INSERT INTO User_Table VALUES (2,'Sara','sara@email.com','Tester');
            INSERT INTO User_Table VALUES (3,'Khalid','khalid@email.com','Manager');
            INSERT INTO User_Table VALUES (4,'Nora','nora@email.com','Developer');
            INSERT INTO User_Table VALUES (5,'Faisal','faisal@email.com','Tester');
            INSERT INTO User_Table VALUES (6,'Maha','maha@email.com','Developer');
            INSERT INTO User_Table VALUES (7,'Omar','omar@email.com','Admin');
            INSERT INTO User_Table VALUES (8,'Laila','laila@email.com','Manager');
            INSERT INTO User_Table VALUES (9,'Hamad','hamad@email.com','Tester');
            INSERT INTO User_Table VALUES (10,'Reem','reem@email.com','Developer');
            INSERT INTO Team VALUES (101,'Frontend');
            INSERT INTO Team VALUES (102,'Backend');
            INSERT INTO Team VALUES (103,'QA');
            INSERT INTO Team VALUES (104,'Security');
            INSERT INTO Team VALUES (105,'Support');
            INSERT INTO Team VALUES (106,'Database');
            INSERT INTO Team VALUES (107,'UIUX');
            INSERT INTO Team VALUES (108,'DevOps');
            INSERT INTO Team VALUES (109,'Mobile');
            INSERT INTO Team VALUES (110,'Analytics');
            INSERT INTO Project VALUES (1001,'Bug Tracker','Tracking issues','2026-01-01','2026-06-30','Active',101);
            INSERT INTO Project VALUES (1002,'Inventory App','Stock system','2026-01-05','2026-07-01','Active',102);
            INSERT INTO Project VALUES (1003,'Portal','Customer portal','2026-02-01','2026-08-01','Pending',103);
            INSERT INTO Project VALUES (1004,'Security Audit','Audit project','2026-02-15','2026-09-01','Active',104);
            INSERT INTO Project VALUES (1005,'Help Desk','Support system','2026-03-01','2026-10-01','Pending',105);
            INSERT INTO Issue VALUES (201,'Login Bug','Password issue','High','Bug','Open','2026-05-01',1001,1);
            INSERT INTO Issue VALUES (202,'UI Error','Button broken','Medium','Bug','Open','2026-05-03',1002,2);
            INSERT INTO Issue VALUES (203,'Server Crash','Downtime issue','High','Incident','Closed','2026-05-04',1003,3);
            INSERT INTO Issue VALUES (204,'Data Loss','Records missing','High','Bug','Open','2026-05-06',1004,4);
            INSERT INTO Issue VALUES (205,'Slow Query','Performance issue','Low','Task','Open','2026-05-08',1005,5);
            INSERT INTO Comment_Table VALUES (301,'Need urgent fix','2026-04-01',1,201);
            INSERT INTO Comment_Table VALUES (302,'Testing in progress','2026-04-02',2,202);
            INSERT INTO Comment_Table VALUES (303,'Issue resolved','2026-04-03',3,203);
            """)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/users", methods=["GET"])
def get_users():
    with get_connection() as conn:
        rows = conn.execute("SELECT User_ID, Name, Email, Role FROM User_Table ORDER BY User_ID").fetchall()
        return jsonify([dict(r) for r in rows])

@app.route("/api/users", methods=["POST"])
def add_user():
    data = request.json
    with get_connection() as conn:
        cur = conn.execute("INSERT INTO User_Table (Name,Email,Role) VALUES (?,?,?)", [data["name"],data["email"],data["role"]])
        return jsonify({"success":True,"id":cur.lastrowid})

@app.route("/api/users/<int:uid>", methods=["PUT"])
def update_user(uid):
    data = request.json
    with get_connection() as conn:
        conn.execute("UPDATE User_Table SET Name=?,Email=?,Role=? WHERE User_ID=?", [data["name"],data["email"],data["role"],uid])
    return jsonify({"success":True})

@app.route("/api/users/<int:uid>", methods=["DELETE"])
def delete_user(uid):
    with get_connection() as conn:
        conn.execute("DELETE FROM User_Table WHERE User_ID=?", [uid])
    return jsonify({"success":True})

@app.route("/api/teams", methods=["GET"])
def get_teams():
    with get_connection() as conn:
        rows = conn.execute("SELECT Team_ID, Team_Name FROM Team ORDER BY Team_ID").fetchall()
        return jsonify([dict(r) for r in rows])

@app.route("/api/teams", methods=["POST"])
def add_team():
    data = request.json
    with get_connection() as conn:
        cur = conn.execute("INSERT INTO Team (Team_Name) VALUES (?)", [data["team_name"]])
        return jsonify({"success":True,"id":cur.lastrowid})

@app.route("/api/teams/<int:tid>", methods=["PUT"])
def update_team(tid):
    data = request.json
    with get_connection() as conn:
        conn.execute("UPDATE Team SET Team_Name=? WHERE Team_ID=?", [data["team_name"],tid])
    return jsonify({"success":True})

@app.route("/api/teams/<int:tid>", methods=["DELETE"])
def delete_team(tid):
    with get_connection() as conn:
        conn.execute("DELETE FROM Team WHERE Team_ID=?", [tid])
    return jsonify({"success":True})

@app.route("/api/projects", methods=["GET"])
def get_projects():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT p.Project_ID, p.Project_Name, p.Description,
                   p.Start_Date, p.End_Date, p.Project_Status, p.Team_ID, t.Team_Name
            FROM Project p LEFT JOIN Team t ON p.Team_ID=t.Team_ID ORDER BY p.Project_ID
        """).fetchall()
        return jsonify([dict(r) for r in rows])

@app.route("/api/projects", methods=["POST"])
def add_project():
    data = request.json
    with get_connection() as conn:
        cur = conn.execute("INSERT INTO Project (Project_Name,Description,Start_Date,End_Date,Project_Status,Team_ID) VALUES (?,?,?,?,?,?)",
            [data["project_name"],data["description"],data["start_date"],data["end_date"],data["project_status"],data["team_id"]])
        return jsonify({"success":True,"id":cur.lastrowid})

@app.route("/api/projects/<int:pid>", methods=["PUT"])
def update_project(pid):
    data = request.json
    with get_connection() as conn:
        conn.execute("UPDATE Project SET Project_Name=?,Description=?,Start_Date=?,End_Date=?,Project_Status=?,Team_ID=? WHERE Project_ID=?",
            [data["project_name"],data["description"],data["start_date"],data["end_date"],data["project_status"],data["team_id"],pid])
    return jsonify({"success":True})

@app.route("/api/projects/<int:pid>", methods=["DELETE"])
def delete_project(pid):
    with get_connection() as conn:
        conn.execute("DELETE FROM Project WHERE Project_ID=?", [pid])
    return jsonify({"success":True})

@app.route("/api/issues", methods=["GET"])
def get_issues():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT i.Issue_ID, i.Title, i.Description, i.Priority, i.Issue_Type, i.Status, i.Due_Date,
                   i.Project_ID, p.Project_Name, i.User_ID, u.Name as Assigned_To
            FROM Issue i
            LEFT JOIN Project p ON i.Project_ID=p.Project_ID
            LEFT JOIN User_Table u ON i.User_ID=u.User_ID ORDER BY i.Issue_ID
        """).fetchall()
        return jsonify([dict(r) for r in rows])

@app.route("/api/issues", methods=["POST"])
def add_issue():
    data = request.json
    with get_connection() as conn:
        cur = conn.execute("INSERT INTO Issue (Title,Description,Priority,Issue_Type,Status,Due_Date,Project_ID,User_ID) VALUES (?,?,?,?,?,?,?,?)",
            [data["title"],data["description"],data["priority"],data["issue_type"],data["status"],data["due_date"],data["project_id"],data["user_id"]])
        return jsonify({"success":True,"id":cur.lastrowid})

@app.route("/api/issues/<int:iid>", methods=["PUT"])
def update_issue(iid):
    data = request.json
    with get_connection() as conn:
        conn.execute("UPDATE Issue SET Title=?,Description=?,Priority=?,Issue_Type=?,Status=?,Due_Date=?,Project_ID=?,User_ID=? WHERE Issue_ID=?",
            [data["title"],data["description"],data["priority"],data["issue_type"],data["status"],data["due_date"],data["project_id"],data["user_id"],iid])
    return jsonify({"success":True})

@app.route("/api/issues/<int:iid>", methods=["DELETE"])
def delete_issue(iid):
    with get_connection() as conn:
        conn.execute("DELETE FROM Issue WHERE Issue_ID=?", [iid])
    return jsonify({"success":True})

@app.route("/api/comments", methods=["GET"])
def get_comments():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT c.Comment_ID, c.Content, c.Date_Posted, c.User_ID,
                   u.Name as User_Name, c.Issue_ID, i.Title as Issue_Title
            FROM Comment_Table c
            LEFT JOIN User_Table u ON c.User_ID=u.User_ID
            LEFT JOIN Issue i ON c.Issue_ID=i.Issue_ID ORDER BY c.Comment_ID
        """).fetchall()
        return jsonify([dict(r) for r in rows])

@app.route("/api/comments", methods=["POST"])
def add_comment():
    data = request.json
    with get_connection() as conn:
        cur = conn.execute("INSERT INTO Comment_Table (Content,Date_Posted,User_ID,Issue_ID) VALUES (?,date('now'),?,?)",
            [data["content"],data["user_id"],data["issue_id"]])
        return jsonify({"success":True,"id":cur.lastrowid})

@app.route("/api/comments/<int:cid>", methods=["DELETE"])
def delete_comment(cid):
    with get_connection() as conn:
        conn.execute("DELETE FROM Comment_Table WHERE Comment_ID=?", [cid])
    return jsonify({"success":True})

@app.route("/api/stats", methods=["GET"])
def get_stats():
    def cnt(conn, sql):
        r = conn.execute(sql).fetchone()
        return list(r.values())[0] if isinstance(r, dict) else r[0]
    with get_connection() as conn:
        return jsonify({
            "users":        cnt(conn, "SELECT COUNT(*) FROM User_Table"),
            "teams":        cnt(conn, "SELECT COUNT(*) FROM Team"),
            "projects":     cnt(conn, "SELECT COUNT(*) FROM Project"),
            "issues":       cnt(conn, "SELECT COUNT(*) FROM Issue"),
            "open_issues":  cnt(conn, "SELECT COUNT(*) FROM Issue WHERE Status='Open'"),
            "high_priority":cnt(conn, "SELECT COUNT(*) FROM Issue WHERE Priority='High'"),
        })

if __name__ == "__main__":
    init_db()
    print("✓ Database ready — http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
