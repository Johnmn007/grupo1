import sys
import os
import random
from datetime import datetime, timedelta, date

# Asegurar importación del proyecto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import (
    Estudiante, Curso, Ciclo, Inscripcion,
    Evaluacion, Nota, Asistencia,
    SeguimientoRiesgo, Intervencion
)

def poblar_datos_prueba():
    app = create_app()

    with app.app_context():
        print("🚀 Iniciando carga de datos de prueba...")

        # ---------------------------------------------------------------------
        # 1. CICLO ACTIVO
        # ---------------------------------------------------------------------
        ciclo = Ciclo.query.filter_by(activo=True).first()
        if not ciclo:
            ciclo = Ciclo(
                nombre="Ciclo I 2025",
                codigo_ciclo="2025-1",
                fecha_inicio=date(2025, 1, 1),
                fecha_fin=date(2025, 6, 30),
                activo=True
            )
            db.session.add(ciclo)
            db.session.commit()
            print("✔ Ciclo creado")

        # ---------------------------------------------------------------------
        # 2. OBTENER ESTUDIANTES Y CURSOS EXISTENTES
        # ---------------------------------------------------------------------
        estudiantes = Estudiante.query.filter_by(activo=True).all()
        cursos = Curso.query.filter_by(activo=True).all()

        if not estudiantes or not cursos:
            print("❌ No hay estudiantes o cursos cargados")
            return

        # ---------------------------------------------------------------------
        # 3. INSCRIPCIONES
        # ---------------------------------------------------------------------
        inscripciones_creadas = 0

        for estudiante in estudiantes:
            for curso in cursos:
                existe = Inscripcion.query.filter_by(
                    estudiante_id=estudiante.id,
                    curso_id=curso.id
                ).first()

                if not existe:
                    ins = Inscripcion(
                        estudiante_id=estudiante.id,
                        curso_id=curso.id,
                        estado="ACTIVO"
                    )
                    db.session.add(ins)
                    inscripciones_creadas += 1

        db.session.commit()
        print(f"✔ Inscripciones creadas: {inscripciones_creadas}")

        # ---------------------------------------------------------------------
        # 4. EVALUACIONES POR CURSO
        # ---------------------------------------------------------------------
        for curso in cursos:
            if not curso.evaluaciones:
                evaluaciones = [
                    ("PC1", "Parcial", 25),
                    ("PC2", "Parcial", 25),
                    ("EX1", "Examen", 25),
                    ("EX2", "Examen", 25),
                ]
                for nombre, tipo, peso in evaluaciones:
                    ev = Evaluacion(
                        curso_id=curso.id,
                        nombre_evaluacion=nombre,
                        tipo_evaluacion=tipo,
                        peso=peso
                    )
                    db.session.add(ev)

        db.session.commit()
        print("✔ Evaluaciones creadas")

        # ---------------------------------------------------------------------
        # 5. NOTAS
        # ---------------------------------------------------------------------
        for inscripcion in Inscripcion.query.all():
            for evaluacion in inscripcion.curso.evaluaciones:
                existe = Nota.query.filter_by(
                    inscripcion_id=inscripcion.id,
                    evaluacion_id=evaluacion.id
                ).first()

                if not existe:
                    nota = Nota(
                        inscripcion_id=inscripcion.id,
                        evaluacion_id=evaluacion.id,
                        nota=round(random.uniform(6, 18), 2)
                    )
                    db.session.add(nota)

        db.session.commit()
        print("✔ Notas generadas")

        # ---------------------------------------------------------------------
        # 6. ASISTENCIAS (20 clases por curso)
        # ---------------------------------------------------------------------
        for inscripcion in Inscripcion.query.all():
            if not inscripcion.asistencias:
                fecha_base = datetime.now() - timedelta(days=60)
                for i in range(20):
                    asistencia = Asistencia(
                        inscripcion_id=inscripcion.id,
                        fecha=fecha_base + timedelta(days=i * 3),
                        presente=random.choice([True, True, True, False])
                    )
                    db.session.add(asistencia)

        db.session.commit()
        print("✔ Asistencias registradas")

        # ---------------------------------------------------------------------
        # 7. SEGUIMIENTO DE RIESGO
        # ---------------------------------------------------------------------
        for estudiante in estudiantes:
            existe = SeguimientoRiesgo.query.filter_by(
                estudiante_id=estudiante.id,
                semestre=ciclo.codigo_ciclo
            ).first()

            if not existe:
                seguimiento = SeguimientoRiesgo(
                    estudiante_id=estudiante.id,
                    semestre=ciclo.codigo_ciclo,
                    categoria_riesgo=random.choice(
                        ["SIN_RIESGO", "ALERTA_AMARILLA", "ALERTA_ROJA"]
                    ),
                    puntaje_riesgo=round(random.uniform(0, 1), 2),
                    factores_riesgo={
                        "rendimiento": random.uniform(0, 1),
                        "asistencia": random.uniform(0, 1),
                        "distribucion": random.uniform(0, 1)
                    }
                )
                db.session.add(seguimiento)

        db.session.commit()
        print("✔ Seguimiento de riesgo creado")

        # ---------------------------------------------------------------------
        # 8. INTERVENCIONES
        # ---------------------------------------------------------------------
        for estudiante in estudiantes[:5]:
            intervencion = Intervencion(
                estudiante_id=estudiante.id,
                tipo_intervencion="Tutoría Académica",
                descripcion="Intervención preventiva por bajo rendimiento",
                responsable="Coordinación Académica",
                estado="PENDIENTE"
            )
            db.session.add(intervencion)

        db.session.commit()
        print("✔ Intervenciones registradas")

        print("\n✅ CARGA DE DATOS DE PRUEBA COMPLETADA")

if __name__ == "__main__":
    poblar_datos_prueba()
