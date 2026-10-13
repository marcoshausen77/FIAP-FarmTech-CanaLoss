-- Referência das operações DML. Usar binds tipados pelo driver, como em src/oracle.py.
-- Executar somente as instruções desejadas; o conjunto não é um script de carga.
INSERT INTO talhoes (id, nome, area_ha) VALUES (:id, :nome, :area);
INSERT INTO colheitas (id, talhao_id, data, area_ha, producao_t, perda_kg_ha, preco_t)
VALUES (:id, :talhao, :data, :area, :producao, :perda, :preco);
SELECT id, nome, area_ha FROM talhoes ORDER BY id;
SELECT id, talhao_id, data, area_ha, producao_t, perda_kg_ha, preco_t
FROM colheitas WHERE talhao_id = :talhao ORDER BY data, id;
UPDATE talhoes SET nome = :nome, area_ha = :area WHERE id = :id;
UPDATE colheitas SET data = :data, producao_t = :producao, perda_kg_ha = :perda,
preco_t = :preco WHERE id = :id;
-- Excluir somente após confirmação explícita. A FK bloqueia talhões com histórico.
DELETE FROM colheitas WHERE id = :id;
DELETE FROM talhoes WHERE id = :id;
-- A aplicação chama connection.commit() somente ao concluir toda a operação;
-- em qualquer erro, chama connection.rollback().
