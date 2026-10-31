# AssetWatch · Monitoreo de condición y confiabilidad industrial

**Ayudar a las organizaciones industriales a conocer el estado de sus activos y priorizar inspecciones mediante información técnica y análisis temporal.**

## Qué resuelve
Recopilar y depurar datos de activos industriales, identificar condiciones anómalas, generar recomendaciones de inspección y documentar su seguimiento por personal de mantenimiento.

Monitoreo de condición de activos: depura telemetría de sensores y emite alertas de revisión explicables con un umbral estadístico robusto (MAD).

## Hacia dónde va
Evolucionar hacia una solución de apoyo al mantenimiento predictivo que permita anticipar riesgos de falla con modelos validados y evidencia de impacto económico.

**Objetivo:** Desarrollar un sistema de análisis de condición que posteriormente pueda evaluarse con sensores y fallas históricas autorizadas, midiendo capacidad de anticipación, falsas alarmas y costo de intervención.

**Valor que persigue:** Mejorar la planificación del mantenimiento y reducir intervenciones innecesarias, sin comprometer la seguridad operacional.

## Resultados de la demo
Sobre un conjunto de datos sintéticos diseñado con errores y casos difíciles: **144 muestras de 2 activos, 1 alerta de revisión por vibración alta persistente (línea base MAD)**.

## Pruébalo en 2 minutos
```bash
python -m venv .venv
source .venv/bin/activate     # Windows: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run.py test     # 19 tests automatizados
python run.py demo     # demo de punta a punta → demo_output/
```

## Diseñado para decisiones responsables
- **Siempre con una persona al mando:** no detiene maquinaria ni emite órdenes de mantenimiento vinculantes; no es control PLC.
- **Trazable:** cada registro conserva su motivo de aceptación, revisión o cuarentena.
- **Probado:** 19 tests automatizados en Linux y Windows en cada cambio.

## Estado
Prototipo funcional demostrado con datos sintéticos. El siguiente paso es un **piloto con datos reales** de su organización, bajo acuerdo de uso y confidencialidad.

**¿Le interesa un piloto?** Contacte a **Kriter Systems**.

---
I16 · Kriter Systems · Los datos incluidos son sintéticos y no representan a personas ni empresas reales.
