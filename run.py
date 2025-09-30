from app import create_app, db, models

app = create_app()

with app.app_context():
    # Cria todas as tabelas
    db.create_all()

    # Cria usuário admin, se não existir
    if not models.Usuario.query.filter_by(email='admin@ifsp.edu.br').first():
        admin = models.Usuario(nome='Admin', email='admin@ifsp.edu.br', tipo='admin', status='ativo')
        admin.set_senha('admin123')
        db.session.add(admin)
        db.session.commit()
        
if __name__ == "__main__":
    app.run(debug=True)
