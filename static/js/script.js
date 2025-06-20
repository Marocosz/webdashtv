// Aguarda o carregamento completo do DOM para configurar todos os event listeners.
document.addEventListener("DOMContentLoaded", function() {

    // --- Seletores de Elementos Globais ---
    const canalSelect = document.getElementById("canal");
    const dataForm = document.getElementById('data-form');
    
    // --- Seletores para o Modal de Edição ---
    const editModal = document.getElementById("edit-modal");
    const openEditModalBtn = document.getElementById("open-edit-modal-btn");
    const closeEditModalBtn = document.getElementById("close-edit-modal-btn");
    const backToListBtn = document.getElementById("back-to-list-btn");
    const saveEditBtn = document.getElementById("save-edit-btn");
    const deleteFromEditBtn = document.getElementById("delete-from-edit-btn");
    const editCanalSelect = document.getElementById('edit-canal');

    // --- Anexando os Event Listeners ---
    if (canalSelect) canalSelect.addEventListener('change', () => updateJornais(canalSelect, document.getElementById('jornal')));
    if (dataForm) dataForm.addEventListener('submit', enviarDados);
    
    // Listeners para o novo modal de edição
    if (openEditModalBtn) openEditModalBtn.addEventListener("click", openEditModal);
    if (closeEditModalBtn) closeEditModalBtn.addEventListener("click", () => { editModal.style.display = "none"; });
    if (backToListBtn) backToListBtn.addEventListener("click", showListView);
    if (saveEditBtn) saveEditBtn.addEventListener("click", saveChanges);
    if (deleteFromEditBtn) deleteFromEditBtn.addEventListener("click", deleteFromEditForm);
    if (editCanalSelect) editCanalSelect.addEventListener('change', () => updateJornais(editCanalSelect, document.getElementById('edit-jornal')));


    // --- Anexar listeners para as funcionalidades antigas ---
    const gerarTextoBtn = document.getElementById('gerar-texto-btn');
    const openDashboardBtn = document.getElementById("open-dashboard-modal-btn");
    const openDownloadExcelBtn = document.getElementById("open-download-excel-modal-btn");
    if(gerarTextoBtn) gerarTextoBtn.addEventListener('click', gerarTextoMensagem);
    if(openDashboardBtn) openDashboardBtn.addEventListener('click', () => document.getElementById('dashboard-modal').style.display = 'flex');
    if(openDownloadExcelBtn) openDownloadExcelBtn.addEventListener('click', () => document.getElementById('download-excel-modal').style.display = 'flex');
    
    const confirmDashboardBtn = document.getElementById("confirm-dashboard-btn");
    if(confirmDashboardBtn) confirmDashboardBtn.addEventListener('click', gerarDashboard);

    const downloadExcelMensalBtn = document.getElementById('download-excel-mensal-btn');
    if(downloadExcelMensalBtn) downloadExcelMensalBtn.addEventListener('click', baixarExcelMensal);

    const baixarExcelCompletoBtn = document.getElementById('download-excel-completo-btn');
    if(baixarExcelCompletoBtn) baixarExcelCompletoBtn.addEventListener('click', baixarExcelCompleto);


    // Fechar modais ao clicar fora
    window.addEventListener("click", function (event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = "none";
        }
    });
});


// --- Funções de Lógica da Aplicação ---

let isSubmitting = false;

function updateJornais(canalElement, jornalElement) {
    const canal = canalElement.value;
    jornalElement.innerHTML = "<option value=''>A carregar...</option>"; 
    
    if (!canal) {
        jornalElement.innerHTML = "<option value=''>Selecione um jornal</option>";
        return;
    }

    fetch('/get_jornais', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ canal: canal })
    })
    .then(response => response.json())
    .then(data => {
        jornalElement.innerHTML = "<option value=''>Selecione um jornal</option>";
        data.forEach(jornal => {
            const option = document.createElement("option");
            option.value = jornal;
            option.textContent = jornal;
            jornalElement.appendChild(option);
        });
    })
    .catch(error => {
        console.error('Erro ao buscar jornais:', error);
        jornalElement.innerHTML = "<option value=''>Erro ao carregar</option>";
    });
}

// --- Novas Funções para Edição e Exclusão ---

async function openEditModal() {
    const modal = document.getElementById('edit-modal');
    const listContainer = document.getElementById('recent-data-list');
    
    modal.style.display = 'flex';
    showListView();
    listContainer.innerHTML = '<p>A carregar dados recentes...</p>';

    try {
        const response = await fetch('/get_recent_data');
        if (!response.ok) throw new Error('Falha ao buscar dados.');
        
        const data = await response.json();
        populateRecentDataList(data);
    } catch (error) {
        listContainer.innerHTML = `<p style="color: red;">${error.message}</p>`;
        console.error(error);
    }
}

function populateRecentDataList(records) {
    const listContainer = document.getElementById('recent-data-list');
    listContainer.innerHTML = '';

    if (records.length === 0) {
        listContainer.innerHTML = '<p>Nenhum registo recente encontrado.</p>';
        return;
    }

    records.forEach(record => {
        const item = document.createElement('div');
        item.className = 'recent-data-item';
        
        item.innerHTML = `
            <div class="item-header">
                <strong>${record.jornal}</strong>
                <span class="item-teor teor-${record.teor}">${record.teor}</span>
            </div>
            <div class="item-meta">
                <span><strong>Canal:</strong> ${record.canal}</span>
                <span><strong>Tema:</strong> ${record.tema}</span>
            </div>
            <p class="item-text">"${record.texto}"</p>
            <div class="item-footer">
                <span>${new Date(record.data_hora).toLocaleString('pt-BR')}</span>
            </div>
        `;
        item.addEventListener('click', () => showEditForm(record));
        listContainer.appendChild(item);
    });
}

function showEditForm(record) {
    document.getElementById('recent-data-container').style.display = 'none';
    document.getElementById('edit-form-container').style.display = 'block';

    document.getElementById('edit-id').value = record.id;
    document.getElementById('edit-canal').value = record.canal;
    document.getElementById('edit-tema').value = record.tema;
    document.getElementById('edit-datahora').value = record.data_hora;
    document.getElementById('edit-teor').value = record.teor;
    document.getElementById('edit-texto').value = record.texto;

    const editCanalSelect = document.getElementById('edit-canal');
    const editJornalSelect = document.getElementById('edit-jornal');
    updateJornais(editCanalSelect, editJornalSelect);
    setTimeout(() => {
        editJornalSelect.value = record.jornal;
    }, 200); 
}

function showListView() {
    document.getElementById('recent-data-container').style.display = 'block';
    document.getElementById('edit-form-container').style.display = 'none';
}

async function saveChanges(event) {
    const button = event.target;
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = 'A Salvar...';

    try {
        const id = document.getElementById('edit-id').value;
        const data = {
            canal: document.getElementById('edit-canal').value,
            jornal: document.getElementById('edit-jornal').value,
            tema: document.getElementById('edit-tema').value,
            data_hora: document.getElementById('edit-datahora').value,
            teor: document.getElementById('edit-teor').value,
            texto: document.getElementById('edit-texto').value,
        };
        
        const response = await fetch(`/update_data/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || 'Erro desconhecido');

        alert(result.message);
        openEditModal();
    } catch (error) {
        alert('Erro ao salvar: ' + error.message);
        console.error(error);
    } finally {
        button.disabled = false;
        button.innerHTML = originalText;
    }
}

async function deleteFromEditForm(event) {
    const button = event.target;
    const originalText = button.innerHTML;
    
    const id = document.getElementById('edit-id').value;
    if (!confirm(`Tem a certeza de que deseja excluir o registo #${id}? Esta ação é irreversível.`)) {
        return;
    }
    
    button.disabled = true;
    button.innerHTML = 'A Excluir...';

    try {
        const response = await fetch(`/delete_data/${id}`, { method: 'DELETE' });
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || 'Erro desconhecido');

        alert(result.message);
        openEditModal();
    } catch (error) {
        alert('Erro ao excluir: ' + error.message);
        console.error(error);
    } finally {
        button.disabled = false;
        button.innerHTML = originalText;
    }
}

async function enviarDados(event) {
    event.preventDefault();
    if (isSubmitting) return;
    isSubmitting = true;

    const form = document.getElementById('data-form');
    const submitButton = form.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.innerHTML;
    submitButton.disabled = true;
    submitButton.innerHTML = 'A Adicionar...';

    const formData = new FormData(form);

    try {
        const response = await fetch('/process', { method: 'POST', body: formData });
        const data = await response.json();
        if (!response.ok) throw new Error(data.message || 'Ocorreu um erro.');
        alert(data.message);
        form.reset();
        updateJornais(document.getElementById('canal'), document.getElementById('jornal'));
    } catch (error) {
        console.error('Erro ao enviar dados:', error);
        alert('Falha ao adicionar dados: ' + error.message);
    } finally {
        submitButton.disabled = false;
        submitButton.innerHTML = originalButtonText;
        isSubmitting = false;
    }
}

async function gerarTextoMensagem(event) {
    const button = event.target;
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = 'A Gerar...';

    try {
        const dataEscolhida = document.getElementById("dataEscolhida").value;
        const periodoEscolhido = document.getElementById("periodo").value;

        if (!dataEscolhida || !periodoEscolhido) {
            throw new Error('Por favor, escolha uma data e um período!');
        }

        const response = await fetch('/gerar_texto_mensagem', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ data: dataEscolhida, periodo: periodoEscolhido })
        });
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'Ocorreu um erro no servidor.');
        }
        
        // CORREÇÃO: Verifica se a chave 'texto' existe na resposta.
        if (data.texto) {
            const novaPagina = window.open('', '_blank');
            novaPagina.document.write('<html><head><title>Clipping</title></head><body><pre>' + data.texto + '</pre></body></html>');
            novaPagina.document.close();
        } else {
            // Se não houver 'texto', mostra a mensagem do servidor (ex: "Nenhum dado encontrado").
            alert(data.message || 'Nenhum texto para exibir.');
        }

    } catch (error) {
        alert('Erro: ' + error.message);
        console.error('Erro ao gerar texto:', error);
    } finally {
        button.disabled = false;
        button.innerHTML = originalText;
    }
}

async function gerarDashboard(event) {
    const button = event.target;
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = "A Gerar...";

    try {
        const mesSelecionado = document.getElementById("mesSelecionado").value;
        if (!mesSelecionado) {
            throw new Error("Selecione um mês antes de gerar o dashboard!");
        }

        const response = await fetch('/gerar_dashboard_pdf', {
            method: 'POST',
            body: JSON.stringify({ mes: mesSelecionado }),
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.erro || 'Erro desconhecido');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `dashboard_mes_${mesSelecionado}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        document.getElementById("dashboard-modal").style.display = "none";

    } catch (error) {
        alert('Erro ao gerar dashboard: ' + error.message);
        console.error(error);
    } finally {
        button.disabled = false;
        button.innerHTML = originalText;
    }
}

async function baixarExcelCompleto(event) {
    const button = event.target;
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = 'A Baixar...';

    try {
        const response = await fetch('/baixar_excel');
        if (!response.ok) throw new Error('Falha na rede ao baixar o arquivo.');
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'dados_completos.xlsx';
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Erro ao baixar Excel completo:', error);
        alert('Erro ao baixar Excel: ' + error.message);
    } finally {
        button.disabled = false;
        button.innerHTML = originalText;
    }
}

async function baixarExcelMensal(event) {
    const button = event.target;
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = 'A Baixar...';
    
    try {
        const mesAno = document.getElementById('mes-ano-excel-mensal').value;
        if (!mesAno) {
            throw new Error('Selecione um mês e ano para o download mensal.');
        }

        const response = await fetch('/baixar-excel-mensal', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mes_ano: mesAno })
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.erro || "Erro ao gerar o Excel.");
        }
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `dados_${mesAno}.xlsx`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        alert("Erro ao tentar baixar o arquivo: " + error.message);
        console.error("Erro no download mensal:", error);
    } finally {
        button.disabled = false;
        button.innerHTML = originalText;
    }
}
