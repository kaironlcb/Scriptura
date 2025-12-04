import sqlite3
import os

DB_NAME = 'literatura.db'

SQL_SCRIPT = """
DROP TABLE IF EXISTS livros;
CREATE TABLE livros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    autor TEXT NOT NULL,
    ano_lancamento INTEGER,
    genero TEXT,
    movimento_literario TEXT,
    caminho_arquivo TEXT UNIQUE NOT NULL,
    caminho_pdf TEXT UNIQUE,
    status TEXT NOT NULL DEFAULT 'PROCESSADO' -- NOVO!
);

-- Todos os nossos 46 livros-base já entram como 'PROCESSADO'
INSERT INTO livros (titulo, autor, ano_lancamento, genero, movimento_literario, caminho_arquivo, caminho_pdf) VALUES
('A Cidade e as Serras', 'Eça de Queiroz', 1901, 'Romance', 'Realismo', 'corpus/a_cidade_e_as_serras.txt', 'static/pdfs/a_cidade_e_as_serras.pdf'),
('A Ilustre Casa de Ramires', 'Eça de Queiroz', 1900, 'Romance', 'Realismo', 'corpus/a_ilustre_casa_de_ramires.txt', 'static/pdfs/a_ilustre_casa_de_ramires.pdf'),
('A Mão e a Luva', 'Machado de Assis', 1874, 'Romance', 'Realismo', 'corpus/a_mao_e_a_luva.txt', 'static/pdfs/a_mao_e_a_luva.pdf'),
('A Moreninha', 'Joaquim Manuel de Macedo', 1844, 'Romance', 'Romantismo', 'corpus/a_moreninha.txt', 'static/pdfs/a_moreninha.pdf'),
('A Pata da Gazela', 'José de Alencar', 1870, 'Romance', 'Romantismo', 'corpus/a_pata_da_gazela.txt', 'static/pdfs/a_pata_da_gazela.pdf'),
('A Relíquia', 'Eça de Queiroz', 1887, 'Romance', 'Realismo', 'corpus/a_reliquia.txt', 'static/pdfs/a_reliquia.pdf'),
('A Viuvinha', 'José de Alencar', 1860, 'Romance', 'Romantismo', 'corpus/a_viuvinha.txt', 'static/pdfs/a_viuvinha.pdf'),
('Americanas', 'Machado de Assis', 1875, 'Poesia', 'Romantismo', 'corpus/americanas.txt', 'static/pdfs/americanas.pdf'),
('Cinco Minutos', 'José de Alencar', 1856, 'Romance', 'Romantismo', 'corpus/cinco_minutos.txt', 'static/pdfs/cinco_minutos.pdf'),
('Contos', 'Eça de Queiroz', 1902, 'Contos', 'Realismo', 'corpus/contos_eca_de_queiroz.txt', 'static/pdfs/contos_eca_de_queiroz.pdf'),
('Contos Fluminenses', 'Machado de Assis', 1870, 'Contos', 'Realismo', 'corpus/contos_fluminenses.txt', 'static/pdfs/contos_fluminenses.pdf'),
('Crisálidas', 'Machado de Assis', 1864, 'Poesia', 'Romantismo', 'corpus/crisalidas.txt', 'static/pdfs/crisalidas.pdf'),
('Diva', 'José de Alencar', 1864, 'Romance', 'Romantismo', 'corpus/diva.txt', 'static/pdfs/diva.pdf'),
('Dom Casmurro', 'Machado de Assis', 1899, 'Romance', 'Realismo', 'corpus/dom_casmurro.txt', 'static/pdfs/dom_casmurro.pdf'),
('Encarnação', 'José de Alencar', 1893, 'Romance', 'Romantismo', 'corpus/encarnacao.txt', 'static/pdfs/encarnacao.pdf'),
('Esaú e Jacó', 'Machado de Assis', 1904, 'Romance', 'Realismo', 'corpus/esau_e_jaco.txt', 'static/pdfs/esau_e_jaco.pdf'),
('Falenas', 'Machado de Assis', 1870, 'Poesia', 'Romantismo', 'corpus/falenas.txt', 'static/pdfs/falenas.pdf'),
('Helena', 'Machado de Assis', 1876, 'Romance', 'Realismo', 'corpus/helena.txt', 'static/pdfs/helena.pdf'),
('Histórias da Meia-Noite', 'Machado de Assis', 1873, 'Contos', 'Realismo', 'corpus/historias_da_meia_noite.txt', 'static/pdfs/historias_da_meia_noite.pdf'),
('Iaiá Garcia', 'Machado de Assis', 1878, 'Romance', 'Realismo', 'corpus/iaia_garcia.txt', 'static/pdfs/iaia_garcia.pdf'),
('Iracema', 'José de Alencar', 1865, 'Romance Indianista', 'Romantismo', 'corpus/iracema.txt', 'static/pdfs/iracema.pdf'),
('Lucíola', 'José de Alencar', 1862, 'Romance', 'Romantismo', 'corpus/luciola.txt', 'static/pdfs/luciola.pdf'),
('Macbeth', 'William Shakespeare', 1606, 'Tragédia', 'Iluminismo', 'corpus/macbeth.txt', 'static/pdfs/macbeth.pdf'),
('Memorial de Aires', 'Machado de Assis', 1908, 'Romance', 'Realismo', 'corpus/memorial_de_aires.txt', 'static/pdfs/memorial_de_aires.pdf'),
('Memórias Póstumas de Brás Cubas', 'Machado de Assis', 1881, 'Romance', 'Realismo', 'corpus/memorias_postumas_de_bras_cubas.txt', 'static/pdfs/memorias_postumas_de_bras_cubas.pdf'),
('Noite na Taverna', 'Álvares de Azevedo', 1855, 'Contos', 'Ultrarromantismo', 'corpus/noite_na_taverna.txt', 'static/pdfs/noite_na_taverna.pdf'),
('O Alienista', 'Machado de Assis', 1882, 'Novela', 'Realismo', 'corpus/o_alienista.txt', 'static/pdfs/o_alienista.pdf'),
('O Cortiço', 'Aluísio Azevedo', 1890, 'Romance', 'Naturalismo', 'corpus/o_cortico.txt', 'static/pdfs/o_cortico.pdf'),
('O Crime do Padre Amaro', 'Eça de Queiroz', 1875, 'Romance', 'Realismo', 'corpus/o_crime_do_padre_amaro.txt', 'static/pdfs/o_crime_do_padre_amaro.pdf'),
('O Gaúcho', 'José de Alencar', 1870, 'Romance Regionalista', 'Romantismo', 'corpus/o_gaucho.txt', 'static/pdfs/o_gaucho.pdf'),
('O Guarani', 'José de Alencar', 1857, 'Romance Indianista', 'Romantismo', 'corpus/o_guarani.txt', 'static/pdfs/o_guarani.pdf'),
('O Mandarim', 'Eça de Queiroz', 1880, 'Novela', 'Realismo', 'corpus/o_mandarim.txt', 'static/pdfs/o_mandarim.pdf'),
('O Primo Basílio', 'Eça de Queiroz', 1878, 'Romance', 'Realismo', 'corpus/o_primo_basilio.txt', 'static/pdfs/o_primo_basilio.pdf'),
('O Sertanejo', 'José de Alencar', 1875, 'Romance Regionalista', 'Romantismo', 'corpus/o_sertanejo.txt', 'static/pdfs/o_sertanejo.pdf'),
('O Tronco do Ipê', 'José de Alencar', 1871, 'Romance Regionalista', 'Romantismo', 'corpus/o_tronco_do_ipe.txt', 'static/pdfs/o_tronco_do_ipe.pdf'),
('Ocidentais', 'Machado de Assis', 1901, 'Poesia', 'Parnasianismo', 'corpus/ocidentais.txt', 'static/pdfs/ocidentais.pdf'),
('Os Maias', 'Eça de Queiroz', 1888, 'Romance', 'Realismo', 'corpus/os_maias.txt', 'static/pdfs/os_maias.pdf'),
('Páginas Recolhidas', 'Machado de Assis', 1899, 'Contos', 'Realismo', 'corpus/paginas_recolhidas.txt', 'static/pdfs/paginas_recolhidas.pdf'),
('Papéis Avulsos', 'Machado de Assis', 1882, 'Contos', 'Realismo', 'corpus/papeis_avulsos.txt', 'static/pdfs/papeis_avulsos.pdf'),
('Poemas de Fernando Pessoa', 'Fernando Pessoa', 1942, 'Poesia', 'Modernismo', 'corpus/poemas_de_fernando_pessoa.txt', 'static/pdfs/poemas_de_fernando_pessoa.pdf'),
('Quincas Borba', 'Machado de Assis', 1891, 'Romance', 'Realismo', 'corpus/quincas_borba.txt', 'static/pdfs/quincas_borba.pdf'),
('Relíquias de Casa Velha', 'Machado de Assis', 1906, 'Contos', 'Realismo', 'corpus/reliquias_de_casa_velha.txt', 'static/pdfs/reliquias_de_casa_velha.pdf'),
('Senhora', 'José de Alencar', 1875, 'Romance', 'Romantismo', 'corpus/senhora.txt', 'static/pdfs/senhora.pdf'),
('Sonhos d''Ouro', 'José de Alencar', 1872, 'Romance', 'Romantismo', 'corpus/sonhos_douro.txt', 'static/pdfs/sonhos_douro.pdf'),
('Til', 'José de Alencar', 1872, 'Romance Regionalista', 'Romantismo', 'corpus/til.txt', 'static/pdfs/til.pdf'),
('Várias Histórias', 'Machado de Assis', 1896, 'Contos', 'Realismo', 'corpus/varias_historias.txt', 'static/pdfs/varias_historias.pdf');
"""

def criar_e_popular_banco():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"Banco de dados antigo '{DB_NAME}' removido.")
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.executescript(SQL_SCRIPT)
        conn.commit()
        print(f"Banco de dados '{DB_NAME}' criado e populado com sucesso.")
    except sqlite3.Error as e:
        print(f"Ocorreu um erro ao criar o banco de dados: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    criar_e_popular_banco()