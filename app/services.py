from sqlalchemy import text

def relatorio_mais_emprestados_sql_puro(db):
    query_sql = """
        SELECT
            o.titulo,
            COUNT(e.id) AS total_emprestimos
        FROM obra o
        JOIN exemplar ex ON o.id = ex.id_obra
        JOIN emprestimo e ON ex.id = e.id_exemplar
        GROUP BY o.id
        ORDER BY total_emprestimos DESC;
    """
    resultado = db.session.execute(text(query_sql))
    return resultado.fetchall()