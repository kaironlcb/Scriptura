document.addEventListener('DOMContentLoaded', () => {
    const API_URL = 'http://127.0.0.1:8000';

    // Segurança simples para TCC
    const senha = prompt("Digite a senha de administrador:");
    if (senha !== "admin123") { // Mude a senha se quiser
        alert("Acesso negado.");
        window.location.href = "home.html";
        return;
    }

    const tabelaBody = document.querySelector('#tabela-livros tbody');
    const modal = document.getElementById('edit-modal');
    const formEdit = document.getElementById('form-edit');
    const btnRefresh = document.getElementById('btn-refresh');
    const btnCancel = document.getElementById('btn-cancel');

    carregarLivros();

    btnRefresh.addEventListener('click', carregarLivros);
    btnCancel.addEventListener('click', () => modal.classList.add('hidden'));

    async function carregarLivros() {
        tabelaBody.innerHTML = '<tr><td colspan="5" style="text-align:center">Carregando...</td></tr>';

        try {
            const response = await fetch(`${API_URL}/admin/listar-todos`);
            const livros = await response.json();

            tabelaBody.innerHTML = '';

            livros.forEach(livro => {
                const tr = document.createElement('tr');

                // Define cor do badge de status
                const statusClass = livro.status === 'PROCESSADO' ? 'status-ok' : 'status-rev';
                const statusLabel = livro.status === 'PROCESSADO' ? 'Aprovado' : 'Revisão';

                tr.innerHTML = `
                    <td>${livro.id}</td>
                    <td><span class="badge ${statusClass}">${statusLabel}</span></td>
                    <td class="col-texto">${livro.titulo}</td>
                    <td class="col-texto">${livro.autor}</td>
                    <td class="actions-cell">
                        <button class="btn-edit" onclick="abrirEdicao(${livro.id})"><i class="fas fa-edit"></i></button>
                        <button class="btn-del" onclick="deletarLivro(${livro.id}, '${livro.titulo}')"><i class="fas fa-trash"></i></button>
                    </td>
                `;
                tabelaBody.appendChild(tr);
            });

            // Necessário para as funções globais (onclick no HTML) funcionarem
            window.livrosCache = livros;

        } catch (error) {
            tabelaBody.innerHTML = '<tr><td colspan="5" style="color:red">Erro ao carregar dados.</td></tr>';
        }
    }

    window.abrirEdicao = (id) => {
        const livro = window.livrosCache.find(l => l.id === id);
        if (!livro) return;

        document.getElementById('edit-id').value = livro.id;
        document.getElementById('edit-titulo').value = livro.titulo;
        document.getElementById('edit-autor').value = livro.autor;
        document.getElementById('edit-status').value = livro.status;

        modal.classList.remove('hidden');
    };

    window.deletarLivro = async (id, titulo) => {
        if (!confirm(`Tem certeza que deseja apagar "${titulo}"?`)) return;

        try {
            await fetch(`${API_URL}/admin/excluir-livro/${id}`, { method: 'DELETE' });
            carregarLivros();
        } catch (error) {
            alert("Erro ao excluir.");
        }
    };

    formEdit.addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('edit-id').value;

        const body = {
            titulo: document.getElementById('edit-titulo').value,
            autor: document.getElementById('edit-autor').value,
            status: document.getElementById('edit-status').value
        };

        try {
            await fetch(`${API_URL}/admin/atualizar-livro/${id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            modal.classList.add('hidden');
            carregarLivros();
        } catch (error) {
            alert("Erro ao atualizar.");
        }
    });
});