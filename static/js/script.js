function enviarDados(event) {
    event.preventDefault();
    const formData = new FormData(document.getElementById('data-form'));

    fetch('/process', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        document.getElementById('data-form').reset();

        // Resetar o campo "Jornal" após adicionar os dados
        let jornalSelect = document.getElementById("jornal");
        jornalSelect.innerHTML = "<option value=''>Selecione um jornal</option>";
    })
    .catch(error => console.error('Erro:', error));
}

function gerarTextoMensagem() {
    const dataEscolhida = document.getElementById("dataEscolhida").value;
    if (!dataEscolhida) {
        alert('Por favor, escolha uma data!');
        return;
    }

    fetch('/gerar_texto_mensagem', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: dataEscolhida })
    })
    .then(response => response.json())
    .then(data => {
        if (data.texto) {
            const novaPagina = window.open('', '_blank');
            novaPagina.document.write('<html><head><title>Clipping de Matérias</title></head><body>');
            novaPagina.document.write('<pre>' + data.texto + '</pre>');
            novaPagina.document.write('</body></html>');
        } else {
            alert('Erro: ' + data.message);
        }
    })
    .catch(error => console.error('Erro ao gerar texto:', error));
}

function gerarDashboard() {
    // Previne o comportamento padrão do formulário
    event.preventDefault();

    // Abre o modal para o mês
    const mesSelecionado = document.getElementById("mesSelecionado").value;

    // Faça a requisição para o backend
    fetch('/gerar_dashboard_pdf', {
        method: 'POST', // ou 'GET' dependendo do seu backend
        body: JSON.stringify({ mes: mesSelecionado }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Erro ao gerar dashboard');
        }
        return response.blob(); // Se for um PDF, vai ser tratado como um Blob
    })
    .then(blob => {
        // Cria um link para o download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'dashboard.pdf'; // Nome do arquivo a ser baixado
        document.body.appendChild(a);
        a.click();
        a.remove();  // Remove o link da página
    })
    .catch(error => console.error('Erro ao gerar o dashboard:', error));
}

function baixarExcel() {
    fetch('/baixar_excel')
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'dados.xlsx';
        document.body.appendChild(a);
        a.click();
        a.remove();
    })
    .catch(error => console.error('Erro ao baixar Excel:', error));
}

function updateJornais() {
    let canal = document.getElementById("canal").value;
    let jornalSelect = document.getElementById("jornal");

    jornalSelect.innerHTML = "<option value=''>Selecione um jornal</option>";
    
    if (!canal) {
        alert("Por favor, selecione um canal antes de escolher um jornal.");
        return;
    }

    fetch('/get_jornais', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({canal: canal})
    })
    .then(response => response.json())
    .then(data => {
        data.forEach(jornal => {
            let option = document.createElement("option");
            option.value = jornal;
            option.textContent = jornal;
            jornalSelect.appendChild(option);
        });
    });
}

document.addEventListener("DOMContentLoaded", function() {
    const modal = document.getElementById("delete-modal");
    const deleteButton = document.getElementById("delete-data");
    const confirmDeleteButton = document.getElementById("confirm-delete");
    const numLinhasInput = document.getElementById("numLinhas");
    const decreaseButton = document.getElementById("decrease");
    const increaseButton = document.getElementById("increase");

    // Abrir modal
    deleteButton.addEventListener("click", function() {
        modal.style.display = "flex";
    });

    // Fechar modal ao clicar fora dele
    window.addEventListener("click", function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });

    // Aumentar o número de linhas a excluir
    increaseButton.addEventListener("click", function() {
        numLinhasInput.value = parseInt(numLinhasInput.value) + 1;
    });

    // Diminuir o número de linhas, mas sem permitir valores menores que 1
    decreaseButton.addEventListener("click", function() {
        if (parseInt(numLinhasInput.value) > 1) {
            numLinhasInput.value = parseInt(numLinhasInput.value) - 1;
        }
    });

    // Evitar valores negativos ou zerados no input manual
    numLinhasInput.addEventListener("input", function() {
        if (numLinhasInput.value < 1) {
            numLinhasInput.value = 1;
        }
    });

    // Confirmar exclusão de linhas
    confirmDeleteButton.addEventListener("click", function() {
        let numLinhas = parseInt(numLinhasInput.value);

        fetch('/delete_last_rows', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }, 
            body: JSON.stringify({ num_linhas: numLinhas })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            modal.style.display = "none"; // Fechar modal após excluir
        })
        .catch(error => console.error('Erro ao excluir linhas:', error));
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const dashboardModal = document.getElementById("dashboard-modal");
    const openDashboardButton = document.getElementById("dashboard-button");
    const confirmDashboardButton = document.getElementById("confirm-dashboard");
    const mesSelecionadoInput = document.getElementById("mesSelecionado");
    const confirmGerarDashButton = document.getElementById("confirm-dashboard");
    
    

    // Abrir modal ao clicar no botão "Gerar Dashboard Mensal"
    openDashboardButton.addEventListener("click", function () {
        dashboardModal.style.display = "flex";
    });

    // Fechar modal ao clicar fora dele
    window.addEventListener("click", function (event) {
        if (event.target === dashboardModal) {
            dashboardModal.style.display = "none";
        }
    });

    // Capturar seleção do mês e fechar modal
    confirmDashboardButton.addEventListener("click", function () {
        if (!mesSelecionadoInput.value) {
            alert("Por favor, selecione um mês.");
            return;
        }

        alert("Dashboard para " + mesSelecionadoInput.value + " será gerado!"); // Substitua por sua lógica real
        dashboardModal.style.display = "none"; // Fechar modal após escolha
    });

    confirmDashboardButton.addEventListener("click", function() {
        let numMes = parseInt(mesSelecionadoInput.value);
        print()
        fetch('/delete_last_rowgerar_dashboard_pdf', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mesSelecionado: numMes })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            modal.style.display = "none"; // Fechar modal após excluir
        })

    });
});

document.getElementById("dashboard-button").addEventListener("click", function(event) {
    event.preventDefault(); // Impede o envio do formulário ou qualquer ação padrão

    // Aqui você pode adicionar a lógica do "Gerar Dashboard Mensal"
    console.log("Gerar Dashboard Mensal clicado!");
});

