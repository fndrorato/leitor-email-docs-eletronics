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
        
        // A variável que conterá o objeto rDE, não o documento completo.
        let dataDE; 

        // --- 2. Lógica para "desembrulhar" (unwrap) o nó rDE ---

        // 2.1. Checagem do Caso SOAP (mais complexo)
        if (parsed['soap:Envelope'] && parsed['soap:Envelope']['soap:Body']) {
            console.log('XML detectado como SOAP Envelope. Desembrulhando...');

            const body = parsed['soap:Envelope']['soap:Body'];
            
            // O próximo nível, 'rEnviDe', não tem prefixo, então use a notação de ponto
            const rEnviDe = body.rEnviDe; 

            if (rEnviDe && rEnviDe.xDE && rEnviDe.xDE.rDE) {
                dataDE = rEnviDe.xDE;
                console.log('Nó rDE encontrado dentro do envelope SOAP.');
            } else {
                return res.status(400).json({ error: 'XML SOAP malformado ou estrutura aninhada inválida.' });
            }
        } 
        // 2.2. Checagem do Caso Lote (rLoteDE)
        else if (parsed.rLoteDE) {
            console.log('XML detectado como Lote (rLoteDE). Desembrulhando...');
            dataDE = parsed.rLoteDE; 

            if (!dataDE) {
                return res.status(400).json({ error: 'XML de Lote malformado: rDE não encontrado dentro de rLoteDE' });
            }

        } 
        // 2.3. Checagem do Caso Documento Único (rDE)
        else if (parsed.rDE) {
            console.log('XML detectado como Documento único (rDE). Usando nó raiz.');
            dataDE = parsed;

        } 
        // 2.4. Caso Inesperado
        else {
            console.log('XML com formato raiz desconhecido.', Object.keys(parsed));
            return res.status(400).json({ error: 'Formato XML raiz inválido. Esperado SOAP, rLoteDE ou rDE.' });
        }         

        const pdfBuffer = await Factura(dataDE, cod_empresa, nome_empresa, logoPath);

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
