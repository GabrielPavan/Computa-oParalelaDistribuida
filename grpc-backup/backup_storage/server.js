const express = require('express');
const fs = require('fs');
const app = express();
const path = require('path');

const PORT = 3000;

app.use(express.json());
app.use(express.static('public'));

const DATA_FILE = './data.json';

// Utilitário para carregar os dados
const getData = () => {
    const data = fs.readFileSync(DATA_FILE);
    return JSON.parse(data);
};

// Rota: Início (listar todos)
app.get('/api/obras', (req, res) => {
    const obras = getData();
    res.json(obras);
});

// Rota: Favoritos
app.get('/api/favoritos', (req, res) => {
    const obras = getData();
    res.json(obras.filter(o => o.kb_favorito === true));
});

app.get('/api/situacao', (req, res) => {
    const obras = getData();
    const filtradas = obras.filter(o => ['hiato', 'finalizado', 'cancelado'].includes(o.kb_situacao));
    res.json(filtradas);
});

app.patch('/api/obras/:id/situacao', (req, res) => {
    const obras = getData();
    const obra = obras.find(o => o._id === req.params.id);
    if (!obra) return res.status(404).json({ erro: 'Obra não encontrada' });

    const { kb_situacao } = req.body;
    obra.kb_situacao = kb_situacao;

    fs.writeFileSync(DATA_FILE, JSON.stringify(obras, null, 2));
    res.json(obra);
});


// Rota: Em Hiato nao usando
app.get('/api/hiato', (req, res) => {
    const obras = getData();
    res.json(obras.filter(o => o.kb_situacao === 'hiato'));
});

// Rota: Cancelado nao usando
app.get('/api/cancelado', (req, res) => {
    const obras = getData();
    res.json(obras.filter(o => o.kb_situacao === 'cancelado'));
});

// Rota: Dropados
app.get('/api/dropados', (req, res) => {
    const obras = getData();
    res.json(obras.filter(o => o.kb_dropado === true));
});

// Rota: Finalizados nao usando
app.get('/api/finalizados', (req, res) => {
    const obras = getData();
    res.json(obras.filter(o => o.kb_situacao === 'finalizado'));
});

// Rota: Adicionar nova obra
app.post('/api/obras', (req, res) => {
    const obras = getData();
    const novaObra = {
        _id: Date.now().toString(),
        kb_published_date: new Date().toISOString(),
        __v: 0,
        ...req.body
    };
    obras.push(novaObra);
    fs.writeFileSync(DATA_FILE, JSON.stringify(obras, null, 2));
    res.status(201).json(novaObra);
});

// Rota: Editar obra por ID
app.put('/api/obras/:id', (req, res) => {
    const obras = getData();
    const obraIndex = obras.findIndex(o => o._id === req.params.id);

    if (obraIndex === -1) {
        return res.status(404).json({ erro: 'Obra não encontrada' });
    }

    obras[obraIndex] = {
        ...obras[obraIndex],
        ...req.body,
        kb_caps: parseInt(req.body.kb_caps) || 0,
        kb_favorito: req.body.kb_favorito === 'true' || req.body.kb_favorito === true,
        kb_dropado: req.body.kb_dropado === 'true' || req.body.kb_dropado === true,
        kb_situacao: req.body.kb_situacao || 'lancando' // garantir que kb_situacao venha
    };

    fs.writeFileSync(DATA_FILE, JSON.stringify(obras, null, 2));
    res.json(obras[obraIndex]);
});


app.delete('/api/obras/:id', (req, res) => {
    const obras = getData();
    const novaLista = obras.filter(o => o._id !== req.params.id);
    fs.writeFileSync(DATA_FILE, JSON.stringify(novaLista, null, 2));
    res.status(204).send();
});

app.patch('/api/obras/:id/capitulo', (req, res) => {
    const obras = getData();
    const obra = obras.find(o => o._id === req.params.id);
    if (!obra) return res.status(404).json({ erro: 'Obra não encontrada' });

    const valor = parseInt(req.body.valor);
    obra.kb_caps += valor;

    fs.writeFileSync(DATA_FILE, JSON.stringify(obras, null, 2));
    res.json(obra);
});

// Atualiza flags (favorito, hiato, dropado) por ID
app.patch('/api/obras/:id/flag', (req, res) => {
    const obras = getData();
    const obra = obras.find(o => o._id === req.params.id);
    if (!obra) return res.status(404).json({ erro: 'Obra não encontrada' });

    const { campo, valor } = req.body;

    if (['kb_favorito', 'kb_hiato', 'kb_dropado', 'kb_finalizado'].includes(campo)) {
        obra[campo] = valor === true || valor === 'true';
        fs.writeFileSync(DATA_FILE, JSON.stringify(obras, null, 2));
        return res.json(obra);
    }

    res.status(400).json({ erro: 'Campo inválido' });
});

app.get('/api/obras/dia/:dia', (req, res) => {
    const dia = req.params.dia.toLowerCase();
    const obras = getData();
    const filtradas = obras.filter(o => (o.kb_dia || '') === dia);
    res.json(filtradas);
});


app.post('/api/importar', express.json(), (req, res) => {
    const novoJson = req.body;
    const fazerBackup = req.query.backup === 'true';

    // backup, cria antes
    if (fazerBackup) {
        const agora = new Date();
        const data = agora.toISOString().split('T')[0];
        const hora = agora.toTimeString().split(' ')[0].replace(/:/g, '-'); // HH-MM-SS
        const backupPath = `./data_backup_${data}_${hora}.json`;
        fs.copyFileSync(DATA_FILE, backupPath);
    }

    // Substitui o arquivo atual
    fs.writeFileSync(DATA_FILE, JSON.stringify(novoJson, null, 2));
    res.status(200).json({ mensagem: 'Importado com sucesso!' });
});

app.post('/api/adicionar-multiplos', express.json(), (req, res) => {
    const novasObras = req.body;

    if (!Array.isArray(novasObras)) {
        return res.status(400).json({ erro: 'Formato inválido. Esperado array de obras.' });
    }

    const fs = require('fs');
    const dataPath = './data.json';
    const dataAtual = JSON.parse(fs.readFileSync(dataPath));

    const novasComID = novasObras.map(o => ({
        ...o,
        _id: Math.random().toString(36).substr(2, 9),
        __v: 0,
        kb_published_date: new Date().toISOString()
    }));

    const atualizado = [...dataAtual, ...novasComID];

    fs.writeFileSync(dataPath, JSON.stringify(atualizado, null, 2));

    res.status(200).json({ mensagem: 'Obras adicionadas!' });
});

// Listar por situação
app.get('/api/situacao/:situacao', (req, res) => {
    const situacao = req.params.situacao.toLowerCase();
    const obras = getData();

    const validas = ['lancando', 'hiato', 'finalizado', 'cancelado'];
    if (!validas.includes(situacao)) {
        return res.status(400).json({ erro: 'Situação inválida.' });
    }

    const filtradas = obras.filter(o => o.kb_situacao === situacao);
    res.json(filtradas);
});

// Atualizar a nota de uma obra
app.patch('/api/obras/:id/nota', (req, res) => {
    const obras = getData();
    const obra = obras.find(o => o._id === req.params.id);

    if (!obra) return res.status(404).json({ erro: 'Obra não encontrada' });

    if (req.body.remover === true) {
        delete obra.kb_nota;
        fs.writeFileSync(DATA_FILE, JSON.stringify(obras, null, 2));
        return res.json({ mensagem: 'Nota removida' });
    }

    const { nota } = req.body;
    if (typeof nota !== 'number' || nota < 0 || nota > 10) {
        return res.status(400).json({ erro: 'Nota inválida. Deve ser um número entre 0 e 10.' });
    }

    obra.kb_nota = nota;
    fs.writeFileSync(DATA_FILE, JSON.stringify(obras, null, 2));
    res.json(obra);
});




app.listen(PORT, () => {
    console.log(`Servidor rodando em http://localhost:${PORT}`);
});
