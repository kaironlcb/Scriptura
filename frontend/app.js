document.addEventListener('DOMContentLoaded', () => {

    const API_URL = 'http://127.0.0.1:8000';

    const formTrecho = document.getElementById('form-trecho');
    const formContexto = document.getElementById('form-contexto');
    const formUpload = document.getElementById('form-upload');

    if (formTrecho) {
        initTrechoPage();
    }
    if (formContexto) {
        initContextoPage();
    }
    if (formUpload) {
        initUploadPage();
    }

    function initTrechoPage() {
        const inputTrecho = document.getElementById('input-trecho');

        formTrecho.addEventListener('submit', async (e) => {
            e.preventDefault();
            const query = inputTrecho.value;
            if (query.length < 5) {
                alert('A busca por trecho deve ter pelo menos 5 caracteres.');
                return;
            }

            const endpoint = `${API_URL}/encontrar-por-trecho`;
            const data = await fetchData(endpoint, { texto: query });

            if (data) {
                displayResults(data, 'trecho');
            }
        });
    }

    function initContextoPage() {
        const inputContexto = document.getElementById('input-contexto');

        formContexto.addEventListener('submit', async (e) => {
            e.preventDefault();
            const query = inputContexto.value;
            if (query.length < 5) {
                alert('A busca por tema deve ter pelo menos 5 caracteres.');
                return;
            }

            const endpoint = `${API_URL}/recomendar-por-tema`;
            const data = await fetchData(endpoint, { texto: query });

            if (data) {
                displayResults(data, 'contexto');
            }
        });
    }

    function initUploadPage() {
        const uploadFile = document.getElementById('upload-file');
        const fileNameDisplay = document.getElementById('file-name-display');

        uploadFile.addEventListener('change', () => {
            if (uploadFile.files.length > 0) {
                fileNameDisplay.textContent = uploadFile.files[0].name;
            } else {
                fileNameDisplay.textContent = 'Nenhum arquivo selecionado';
            }
        });

        formUpload.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData();
            formData.append('titulo', document.getElementById('upload-titulo').value);
            formData.append('autor', document.getElementById('upload-autor').value);
            formData.append('file', uploadFile.files[0]);

            const ano = document.getElementById('upload-ano').value;
            const genero = document.getElementById('upload-genero').value;
            const movimento = document.getElementById('upload-movimento').value;

            if (ano) formData.append('ano_lancamento', ano);
            if (genero) formData.append('genero', genero);
            if (movimento) formData.append('movimento_literario', movimento);

            const uploadMessage = document.getElementById('upload-message');
            uploadMessage.innerHTML = '';

            try {
                const response = await fetch(`${API_URL}/upload-livro`, {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (!response.ok) {
                    throw new Error(result.detail || 'Erro desconhecido no upload.');
                }

                uploadMessage.className = 'message-success';
                uploadMessage.innerText = `Sucesso! "${result.titulo}" foi enviado para revisão.`;
                formUpload.reset();
                fileNameDisplay.textContent = 'Nenhum arquivo selecionado';

            } catch (error) {
                uploadMessage.className = 'message-error';
                uploadMessage.innerText = `Erro: ${error.message}`;
            }
        });
    }

    async function fetchData(endpoint, bodyPayload) {
        const resultsSidebar = document.getElementById('results-sidebar');
        const metadataSidebar = document.getElementById('metadata-sidebar');
        const resultsContainer = document.getElementById('results-container');
        if (!resultsContainer) {
            console.error("Bug fatal: #results-container não encontrado.");
            return;
        }

        resultsContainer.innerHTML = '<h4>Buscando...</h4>';

        resultsSidebar.classList.remove('hidden');
        metadataSidebar.classList.add('hidden');

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(bodyPayload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Erro HTTP: ${response.status}`);
            }

            return await response.json();

        } catch (error) {
            resultsContainer.innerHTML = `<p class="message-error"><b>Erro:</b> ${error.message}</p>`;
            return null;
        }
    }

    function displayResults(results, type) {
        const resultsContainer = document.getElementById('results-container');
        resultsContainer.innerHTML = '';

        if (results.length === 0) {
            resultsContainer.innerHTML = '<p>Nenhum resultado encontrado.</p>';
            return;
        }

        const groups = {};
        results.forEach(result => {
            const obraId = result.obra.id;
            if (!groups[obraId]) {
                groups[obraId] = {
                    obra: result.obra,
                    trechos: []
                };
            }

            const texto = (type === 'trecho') ? result.texto_encontrado : result.texto_chunk_encontrado;
            groups[obraId].trechos.push(texto);
        });

        const allGroups = Object.values(groups);

        allGroups.forEach(group => {
            const groupDiv = document.createElement('div');
            groupDiv.className = 'result-group';

            const title = document.createElement('h4');
            title.innerText = group.obra.titulo;

            title.addEventListener('click', () => {
                if (type === 'contexto') {
                    displayMetadata(group);
                } else {
                    displayMetadata(group.obra);
                }
            });

            groupDiv.appendChild(title);

            if (type === 'trecho') {
                const trechosLimitados = group.trechos.slice(0, 5);
                trechosLimitados.forEach(texto => {
                    const trechoP = document.createElement('p');
                    trechoP.innerText = `"${texto}"`;
                    groupDiv.appendChild(trechoP);
                });
            }

            resultsContainer.appendChild(groupDiv);
        });
    }

    function displayMetadata(data) {
        const metadataSidebar = document.getElementById('metadata-sidebar');
        const metadataContainer = document.getElementById('metadata-container');
        metadataContainer.innerHTML = '';


        let obra;
        let trechos = null;

        if (data.trechos) {
            obra = data.obra;
            trechos = data.trechos;
            metadataSidebar.classList.add('metadata-box-expanded');
        } else {
            obra = data;
            metadataSidebar.classList.remove('metadata-box-expanded');
        }

        metadataContainer.innerHTML += `<div class="metadata-item"><b>Obra:</b> ${obra.titulo || 'N/A'}</div>`;
        metadataContainer.innerHTML += `<div class="metadata-item"><b>Autor:</b> ${obra.autor || 'N/A'}</div>`;
        metadataContainer.innerHTML += `<div class="metadata-item"><b>Ano:</b> ${obra.ano_lancamento || 'N/A'}</div>`;
        metadataContainer.innerHTML += `<div class="metadata-item"><b>G&ecirc;nero:</b> ${obra.genero || 'N/A'}</div>`;
        metadataContainer.innerHTML += `<div class="metadata-item"><b>Movimento:</b> ${obra.movimento_literario || 'N/A'}</div>`;

        if (obra.url_download) {
            metadataContainer.innerHTML += `<a href="${API_URL}${obra.url_download}" target="_blank" class="metadata-item download-link">Clique aqui para baixar o PDF</a>`;
        }

        if (trechos) {
            metadataContainer.innerHTML += '<hr class="metadata-divider">';
            metadataContainer.innerHTML += '<b class="metadata-trechos-title">Trechos Relevantes:</b>';

            const trechosDiv = document.createElement('div');
            trechosDiv.className = 'metadata-trechos-list';

            trechos.forEach(texto => {
                const trechoP = document.createElement('p');
                trechoP.innerText = `"${texto}"`;
                trechosDiv.appendChild(trechoP);
            });
            metadataContainer.appendChild(trechosDiv);
        }

        metadataSidebar.classList.remove('hidden');
    }

});