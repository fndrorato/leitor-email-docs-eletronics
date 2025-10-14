const express = require('express');
const router = express.Router();
const path = require('path');
const { Factura } = require('../services/Factura');
const { NotaCredito } = require('../services/NotaCredito'); // Importa o serviço NotaCredito
const { parseStringPromise } = require('xml2js');
const xml2js = require('xml2js'); // Este import não está sendo usado, pode ser removido se não for necessário em outro lugar

router.post('/factura', async (req, res) => {
    try {
        const { xml, cod_empresa, nome_empresa } = req.body;

        if (!xml || !cod_empresa || !nome_empresa) {
            return res.status(400).json({ error: 'Dados incompletos' });
        }

        // Converte XML para JSON
        const parsed = await parseStringPromise(xml, { explicitArray: false });

        // Constrói o caminho absoluto para o logo de forma mais robusta
        const projectRoot = path.resolve(__dirname, '..'); 
        const logoPath = path.join(projectRoot, 'media', 'logoFactura.png');

        // Log para verificar o caminho final do logo antes de passar para a função Factura
        console.log('Caminho do logo da Fatura na rota:', logoPath);

        let data; // Esta variável será o nosso nó rDE final

        // 2. Lógica para "desembrulhar" (unwrap) o nó rDE
        if (parsed.rLoteDE) {
            // Caso 1: O XML começa com <rLoteDE>, que é o nó raiz
            console.log('XML detectado como Lote (rLoteDE). Desembrulhando...');
            
            // O nó real que nos interessa (rDE) estará dentro de rLoteDE
            dataParsed = parsed.rLoteDE; 

            if (!dataParsed) {
                // Checagem de segurança caso rLoteDE esteja vazio ou malformado
                return res.status(400).json({ error: 'XML de Lote malformado: rDE não encontrado dentro de rLoteDE' });
            }

        } else if (parsed.rDE) {
            // Caso 2: O XML começa diretamente com <rDE>, que é o nó raiz
            console.log('XML detectado como Documento único (rDE). Usando nó raiz.');
            dataParsed = parsed;

        } else {
            // Caso 3: Não é rLoteDE nem rDE (XML totalmente inesperado)
            console.log('XML com formato raiz desconhecido.', Object.keys(parsed));
            return res.status(400).json({ error: 'Formato XML raiz inválido. Esperado rLoteDE ou rDE.' });
        }        

        const pdfBuffer = await Factura(dataParsed, cod_empresa, nome_empresa, logoPath);

        res.setHeader('Content-Type', 'application/pdf');
        res.setHeader('Content-Disposition', 'inline; filename=factura.pdf');
        return res.send(pdfBuffer);
    } catch (err) {
        console.error('Erro na rota /factura:', err);
        return res.status(500).json({ error: 'Erro ao gerar PDF da Fatura', details: err.message });
    }
});

router.post('/notacredito', async (req, res) => { // Nova rota para Nota de Crédito
    try {
        const { xml, cod_empresa, nome_empresa } = req.body;

        if (!xml || !cod_empresa || !nome_empresa) {
            return res.status(400).json({ error: 'Dados incompletos' });
        }

        // Converte XML para JSON
        const parsed = await parseStringPromise(xml, { explicitArray: false });

        // Constrói o caminho absoluto para o logo da Nota de Crédito
        const projectRoot = path.resolve(__dirname, '..'); 
        const logoPath = path.join(projectRoot, 'media', 'logoNotaCredito.png'); // Caminho para o logo da Nota de Crédito

        // Log para verificar o caminho final do logo antes de passar para a função NotaCredito
        console.log('Caminho do logo da Nota de Crédito na rota:', logoPath);

        // Chama o serviço NotaCredito
        const pdfBuffer = await NotaCredito(parsed, cod_empresa, nome_empresa, logoPath);

        res.setHeader('Content-Type', 'application/pdf');
        res.setHeader('Content-Disposition', 'inline; filename=nota_credito.pdf'); // Nome do arquivo PDF
        return res.send(pdfBuffer);
    } catch (err) {
        console.error('Erro na rota /notacredito:', err);
        return res.status(500).json({ error: 'Erro ao gerar PDF da Nota de Crédito', details: err.message });
    }
});

module.exports = router;
