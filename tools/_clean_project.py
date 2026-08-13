import sqlite3

conn = sqlite3.connect("central_intelligence.db")
row = conn.execute("SELECT id, name FROM projects WHERE slug = 'cafe-cenit'").fetchone()
if row:
    pid = row[0]
    print(f"Limpiando proyecto: {row[1]} (id={pid})")
    conn.execute("DELETE FROM execution_logs WHERE project_id = ?", (pid,))
    conn.execute("DELETE FROM artifacts WHERE project_id = ?", (pid,))
    conn.execute("DELETE FROM checkpoints WHERE project_id = ?", (pid,))
    conn.execute("DELETE FROM feedback_history WHERE project_id = ?", (pid,))
    conn.execute("DELETE FROM tasks WHERE project_id = ?", (pid,))
    conn.execute("DELETE FROM projects WHERE id = ?", (pid,))
    conn.commit()
    print("Proyecto eliminado completamente.")
else:
    print("No existe proyecto previo.")
conn.close()
