# Pruebas SQL — MySQL (Cochabamba)

Scripts de **laboratorio**; no se ejecutan en el arranque automático.

| Archivo | Propósito |
|---------|-----------|
| `optimizacion_explain.sql` | `ANALYZE TABLE`, `EXPLAIN ANALYZE` (requiere `apply_benchmark_seed.py` antes) |
| `transacciones_concurrencia.sql` | Índice a `07_transacciones.sql` |
| `deadlock_demo.sql` | Deadlock manual (2 terminales) |

Documentación: [`../../README.md`](../../README.md), [`../../../docs/conectividad_red.md`](../../../docs/conectividad_red.md).

```bash
cd database
mysql -h localhost -P 3306 -u sicc_admin -psicc_mysql_pass_2024 sicc_cochabamba < mysql/test/optimizacion_explain.sql
```

Requiere `06_vistas_procedimientos.sql` aplicado (`init_databases.py` o manual).
