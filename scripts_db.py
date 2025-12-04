# scripts_db.py
import sqlite3
import os

DB_NAME = 'literatura.db'

# --- Nosso script SQL completo com os 88 livros ---
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
    caminho_pdf TEXT UNIQUE
);


INSERT INTO livros (titulo, autor, ano_lancamento, genero, movimento_literario, caminho_arquivo, caminho_pdf) VALUES
('A Mão e a Luva', 'Machado de Assis', 1874, 'Romance', 'Realismo', 'corpus/a_mao_e_a_luva.txt', 'static/pdfs/a_mao_e_a_luva.pdf'),
('A Moreninha', 'Joaquim Manuel de Macedo', 1844, 'Romance', 'Romantismo', 'corpus/a_moreninha.txt', 'static/pdfs/a_moreninha.pdf'),
('A Pata da Gazela', 'José de Alencar', 1870, 'Romance', 'Romantismo', 'corpus/a_pata_da_gazela.txt', 'static/pdfs/a_pata_da_gazela.pdf'),
('A Viuvinha', 'José de Alencar', 1860, 'Romance', 'Romantismo', 'corpus/a_viuvinha.txt', 'static/pdfs/a_viuvinha.pdf'),
('Americanas', 'Machado de Assis', 1875, 'Poesia', 'Romantismo', 'corpus/americanas.txt', 'static/pdfs/americanas.pdf'),
('Cinco Minutos', 'José de Alencar', 1856, 'Romance', 'Romantismo', 'corpus/cinco_minutos.txt', 'static/pdfs/cinco_minutos.pdf'),
('Contos Fluminenses', 'Machado de Assis', 1870, 'Contos', 'Realismo', 'corpus/contos_fluminenses.txt', 'static/pdfs/contos_fluminenses.pdf'),
('Crisálidas', 'Machado de Assis', 1864, 'Poesia', 'Romantismo', 'corpus/crisalidas.txt', 'static/pdfs/crisalidas.pdf'),
('Diva', 'José de Alencar', 1864, 'Romance', 'Romantismo', 'corpus/diva.txt', 'static/pdfs/diva.pdf'),
('Encarnação', 'José de Alencar', 1893, 'Romance', 'Romantismo', 'corpus/encarnacao.txt', 'static/pdfs/encarnacao.pdf'),
('Esaú e Jacó', 'Machado de Assis', 1904, 'Romance', 'Realismo', 'corpus/esau_e_jaco.txt', 'static/pdfs/esau_e_jaco.pdf'),
('Falenas', 'Machado de Assis', 1870, 'Poesia', 'Romantismo', 'corpus/falenas.txt', 'static/pdfs/falenas.pdf'),
('Helena', 'Machado de Assis', 1876, 'Romance', 'Realismo', 'corpus/helena.txt', 'static/pdfs/helena.pdf'),
('Histórias da Meia-Noite', 'Machado de Assis', 1873, 'Contos', 'Realismo', 'corpus/historias_da_meia_noite.txt', 'static/pdfs/historias_da_meia_noite.pdf'),
('Iaiá Garcia', 'Machado de Assis', 1878, 'Romance', 'Realismo', 'corpus/iaia_garcia.txt', 'static/pdfs/iaia_garcia.pdf'),
('Iracema', 'José de Alencar', 1865, 'Romance Indianista', 'Romantismo', 'corpus/iracema.txt', 'static/pdfs/iracema.pdf'),
('Lucíola', 'José de Alencar', 1862, 'Romance', 'Romantismo', 'corpus/luciola.txt', 'static/pdfs/luciola.pdf'),
('Memorial de Aires', 'Machado de Assis', 1908, 'Romance', 'Realismo', 'corpus/memorial_de_aires.txt', 'static/pdfs/memorial_de_aires.pdf'),
('Memórias Póstumas de Brás Cubas', 'Machado de Assis', 1881, 'Romance', 'Realismo', 'corpus/memorias_postumas_de_bras_cubas.txt', 'static/pdfs/memorias_postumas_de_bras_cubas.pdf'),
('O Guarani', 'José de Alencar', 1857, 'Romance Indianista', 'Romantismo', 'corpus/o_guarani.txt', 'static/pdfs/o_guarani.pdf'),
('O Alienista', 'Machado de Assis', 1882, 'Novela', 'Realismo', 'corpus/o_alienista.txt', 'static/pdfs/o_alienista.pdf'),
('O Gaúcho', 'José de Alencar', 1870, 'Romance Regionalista', 'Romantismo', 'corpus/o_gaucho.txt', 'static/pdfs/o_gaucho.pdf'),
('O Sertanejo', 'José de Alencar', 1875, 'Romance Regionalista', 'Romantismo', 'corpus/o_sertanejo.txt', 'static/pdfs/o_sertanejo.pdf'),
('O Tronco do Ipê', 'José de Alencar', 1871, 'Romance Regionalista', 'Romantismo', 'corpus/o_tronco_do_ipe.txt', 'static/pdfs/o_tronco_do_ipe.pdf'),
('Ocidentais', 'Machado de Assis', 1901, 'Poesia', 'Parnasianismo', 'corpus/ocidentais.txt', 'static/pdfs/ocidentais.pdf'),
('Papéis Avulsos', 'Machado de Assis', 1882, 'Contos', 'Realismo', 'corpus/papeis_avulsos.txt', 'static/pdfs/papeis_avulsos.pdf'),
('Páginas Recolhidas', 'Machado de Assis', 1899, 'Contos', 'Realismo', 'corpus/paginas_recolhidas.txt', 'static/pdfs/paginas_recolhidas.pdf'),
('Quincas Borba', 'Machado de Assis', 1891, 'Romance', 'Realismo', 'corpus/quincas_borba.txt', 'static/pdfs/quincas_borba.pdf'),
('Relíquias de Casa Velha', 'Machado de Assis', 1906, 'Contos', 'Realismo', 'corpus/reliquias_de_casa_velha.txt', 'static/pdfs/reliquias_de_casa_velha.pdf'),
('Senhora', 'José de Alencar', 1875, 'Romance', 'Romantismo', 'corpus/senhora.txt', 'static/pdfs/senhora.pdf'),
('Sonhos d''Ouro', 'José de Alencar', 1872, 'Romance', 'Romantismo', 'corpus/sonhos_douro.txt', 'static/pdfs/sonhos_douro.pdf'),
('Til', 'José de Alencar', 1872, 'Romance Regionalista', 'Romantismo', 'corpus/til.txt', 'static/pdfs/til.pdf'),
('Várias Histórias', 'Machado de Assis', 1896, 'Contos', 'Realismo', 'corpus/varias_historias.txt', 'static/pdfs/varias_historias.pdf'),
('A Cidade e as Serras', 'Eça de Queiroz', 1901, 'Romance', 'Realismo', 'corpus/a_cidade_e_as_serras.txt', 'static/pdfs/a_cidade_e_as_serras.pdf'),
('A Ilustre Casa de Ramires', 'Eça de Queiroz', 1900, 'Romance', 'Realismo', 'corpus/a_ilustre_casa_de_ramires.txt', 'static/pdfs/a_ilustre_casa_de_ramires.pdf'),
('A Relíquia', 'Eça de Queiroz', 1887, 'Romance', 'Realismo', 'corpus/a_reliquia.txt', 'static/pdfs/a_reliquia.pdf'),
('Contos', 'Eça de Queiroz', 1902, 'Contos', 'Realismo', 'corpus/contos_eca_de_queiroz.txt', 'static/pdfs/contos_eca_de_queiroz.pdf'),
('O Crime do Padre Amaro', 'Eça de Queiroz', 1875, 'Romance', 'Realismo', 'corpus/o_crime_do_padre_amaro.txt', 'static/pdfs/o_crime_do_padre_amaro.pdf'),
('O Mandarim', 'Eça de Queiroz', 1880, 'Novela', 'Realismo', 'corpus/o_mandarim.txt', 'static/pdfs/o_mandarim.pdf'),
('O Primo Basílio', 'Eça de Queiroz', 1878, 'Romance', 'Realismo', 'corpus/o_primo_basilio.txt', 'static/pdfs/o_primo_basilio.pdf'),
('Os Maias', 'Eça de Queiroz', 1888, 'Romance', 'Realismo', 'corpus/os_maias.txt', 'static/pdfs/os_maias.pdf'),
('Poesias Completas', 'Álvares de Azevedo', 1886, 'Poesia', 'Ultrarromantismo', 'corpus/poesias_completas_alvares_azevedo.txt', 'static/pdfs/poesias_completas_alvares_azevedo.pdf'),
('Lira dos Vinte Anos', 'Álvares de Azevedo', 1853, 'Poesia', 'Ultrarromantismo', 'corpus/lira_dos_vinte_anos.txt', 'static/pdfs/lira_dos_vinte_anos.pdf'),
('Noite na Taverna', 'Álvares de Azevedo', 1855, 'Contos', 'Ultrarromantismo', 'corpus/noite_na_taverna.txt', 'static/pdfs/noite_na_taverna.pdf'),
('Dom Casmurro', 'Machado de Assis', 1899, 'Romance', 'Realismo', 'corpus/dom_casmurro.txt', 'static/pdfs/dom_casmurro.pdf'),
('A Escrava Isaura', 'Bernardo Guimarães', 1875, 'Romance', 'Romantismo', 'corpus/a_escrava_isaura.txt', 'static/pdfs/a_escrava_isaura.pdf'),
('O Seminarista', 'Bernardo Guimarães', 1872, 'Romance', 'Romantismo', 'corpus/o_seminarista.txt', 'static/pdfs/o_seminarista.pdf'),
('A Divina Comédia', 'Dante Alighieri', 1321, 'Poesia Narrativa', 'Humanismo', 'corpus/a_divina_comedia.txt', 'static/pdfs/a_divina_comedia.pdf'),
('Poemas de Fernando Pessoa', 'Fernando Pessoa', 1942, 'Poesia', 'Modernismo', 'corpus/poemas_de_fernando_pessoa.txt', 'static/pdfs/poemas_de_fernando_pessoa.pdf'),
('Mensagem', 'Fernando Pessoa', 1934, 'Poesia', 'Modernismo', 'corpus/mensagem.txt', 'static/pdfs/mensagem.pdf'),
('A Cartomante', 'Machado de Assis', 1884, 'Conto', 'Realismo', 'corpus/a_cartomante.txt', 'static/pdfs/a_cartomante.pdf'),
('A Metamorfose', 'Franz Kafka', 1915, 'Novela', 'Absurdismo', 'corpus/a_metamorfose.txt', 'static/pdfs/a_metamorfose.pdf'),
('O Eu profundo e os outros Eus', 'Fernando Pessoa', 1888, 'Poesia', 'Modernismo', 'corpus/o_eu_profundo_e_os_outros_eus.txt', 'static/pdfs/o_eu_profundo_e_os_outros_eus.pdf'),
('Poesias Inéditas', 'Fernando Pessoa', 1935, 'Poesia','Modernismo', 'corpus/poesias_ineditas.txt', 'static/pdfs/poesias_ineditas.pdf'),
('Do Livro do Desassossego', 'Fernando Pessoa', 1982, 'Romance', 'Modernismo', 'corpus/do_livro_do_desassossego.txt', 'static/pdfs/do_livro_do_desassossego.pdf'),
('Cancioneiro', 'Fernando Pessoa', 1930, 'Poesia', 'Modernismo', 'corpus/cancioneiro.txt', 'static/pdfs/cancioneiro.pdf'),
('A Igreja do Diabo', 'Machado de Assis', 1884, 'Conto', 'Realismo', 'corpus/a_igreja_do_diabo.txt', 'static/pdfs/a_igreja_do_diabo.pdf'),
('A Carteira', 'Machado de Assis', 1884, 'Conto', 'Realismo', 'corpus/a_carteira.txt', 'static/pdfs/a_carteira.pdf'),
('Os Lusíadas', 'Luís Vaz de Camões', 1572, 'Poema Épico', 'Classicismo', 'corpus/os_lusiadas.txt', 'static/pdfs/os_lusiadas.pdf'),
('O pastor amoroso', 'Fernando Pessoa', 1930, 'Poesia', 'Modernismo', 'corpus/o_pastor_amoroso.txt', 'static/pdfs/o_pastor_amoroso.pdf'),
('O Cortiço', 'Aluísio Azevedo', 1890, 'Romance', 'Naturalismo', 'corpus/o_cortico.txt', 'static/pdfs/o_cortico.pdf'),
('Macbeth', 'William Shakespeare', 1606, 'Tragédia', 'Iluminismo', 'corpus/macbeth.txt', 'static/pdfs/macbeth.pdf'),
('O Mercador de Veneza', 'William Shakespeare', 1598, 'Comédia', 'Iluminismo', 'corpus/o_mercador_de_veneza.txt', 'static/pdfs/o_mercador_de_veneza.pdf'),
('A Carta', 'Pero Vaz de Caminha', 1500, 'Relato', 'Quinhentismo', 'corpus/a_carta.txt', 'static/pdfs/a_carta.pdf'),
('O Guardador de Rebanhos', 'Fernando Pessoa', 1914, 'Poesia', 'Modernismo', 'corpus/o_guardador_de_rebanhos.txt', 'static/pdfs/o_guardador_de_rebanhos.pdf'),
('Arte Poética', 'Aristóteles', -323, 'Poesia', 'Período Clássico Grego', 'corpus/arte_poetica.txt', 'static/pdfs/arte_poetica.pdf'),
('A Volta ao Mundo em 80 Dias', 'Júlio Verne', 1873, 'Aventura', 'Romantismo', 'corpus/a_volta_ao_mundo_em_80_dias.txt', 'static/pdfs/a_volta_ao_mundo_em_80_dias.pdf'),
('Este mundo da injustiça globalizada', 'José Saramago', 2002, 'Discurso', 'Contemporâneo', 'corpus/este_mundo_da_injustica_globalizada.txt', 'static/pdfs/este_mundo_da_injustica_globalizada.pdf'),
('Fausto', 'Johann Wolfgang von Goethe', 1832, 'Tragédia', 'Romantismo alemão', 'corpus/fausto.txt', 'static/pdfs/fausto.pdf'),
('Don Quixote. Vol. 1', 'Miguel de Cervantes Saavedra', 1605, 'Romance', 'Barroco', 'corpus/don_quixote_vol_1.txt', 'static/pdfs/don_quixote_vol_1.pdf'),
('Utopia', 'Thomas Morus', 1516, 'Narrativa Utópica', 'Renascimento', 'corpus/utopia.txt', 'static/pdfs/utopia.pdf'),
('Auto da Barca do Inferno', 'Gil Vicente', 1517, 'Teatro', 'Humanismo', 'corpus/auto_da_barca_do_inferno.txt', 'static/pdfs/auto_da_barca_do_inferno.pdf'),
('O Espelho', 'Machado de Assis', 1882, 'Conto', 'Realismo', 'corpus/o_espelho.txt', 'static/pdfs/o_espelho.pdf'),
('Poemas Traduzidos', 'Fernando Pessoa', 1938, 'Poesia', 'Modernismo', 'corpus/poemas_traduzidos.txt', 'static/pdfs/poemas_traduzidos.pdf'),
('Os Sertões', 'Euclides da Cunha', 1902, 'Crônica', 'Pré-Modernismo', 'corpus/os_sertoes.txt', 'static/pdfs/os_sertoes.pdf'),
('Pai Contra Mãe', 'Machado de Assis', 1906, 'Conto', 'Realismo', 'corpus/pai_contra_mae.txt', 'static/pdfs/pai_contra_mae.pdf'),
('O Banqueiro Anarquista', 'Fernando Pessoa', 1922, 'Conto', 'Modernismo', 'corpus/o_banqueiro_anarquista.txt', 'static/pdfs/o_banqueiro_anarquista.pdf'),
('Édipo-Rei', 'Sófocles', -427, 'Teatro', 'Tragédia Grega', 'corpus/edipo_rei.txt', 'static/pdfs/edipo_rei.pdf'),
('A Alma Encantadora das Ruas', 'João do Rio', 1908, 'Crônicas', 'Decadentismo', 'corpus/a_alma_encantadora_das_ruas.txt', 'static/pdfs/a_alma_encantadora_das_ruas.pdf'),
('A Causa Secreta', 'Machado de Assis', 1885, 'Conto', 'Realismo', 'corpus/a_causa_secreta.txt', 'static/pdfs/a_causa_secreta.pdf'),
('A Esfinge sem Segredo', 'Oscar Wilde', 1887, 'Conto', 'Esteticismo', 'corpus/a_esfinge_sem_segredo.txt', 'static/pdfs/a_esfinge_sem_segredo.pdf'),
('O Ermitão da Glória', 'José de Alencar', 1873, 'Ficção brasileira', 'Romantismo', 'corpus/o_ermitao_da_gloria.txt', 'static/pdfs/o_ermitao_da_gloria.pdf');
"""

def criar_e_popular_banco():
    """
    Cria e popula o banco de dados SQLite a partir do script SQL.
    Apaga o banco de dados antigo se ele existir para garantir um novo começo.
    """
    # Apaga o arquivo de banco de dados antigo, se existir, para garantir uma recriação limpa.
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"Banco de dados antigo '{DB_NAME}' removido.")

    try:
        # Conecta ao banco (isso criará o arquivo .db)
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Executa todo o script SQL de uma vez
        cursor.executescript(SQL_SCRIPT)
        
        # Salva as alterações
        conn.commit()
        print(f"Banco de dados '{DB_NAME}' criado e populado com sucesso!")
        
    except sqlite3.Error as e:
        print(f"Ocorreu um erro ao criar o banco de dados: {e}")
        
    finally:
        # Garante que a conexão seja fechada
        if conn:
            conn.close()

if __name__ == '__main__':
    criar_e_popular_banco()