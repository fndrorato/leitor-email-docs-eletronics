const { jsPDF } = require('jspdf');
require('jspdf-autotable'); // jspdf-autotable extends jsPDF automatically

const accounting = require('accounting');
const moment = require('moment');
const num2word = require('../utils/num2word');
const _ = require('underscore'); // Used for utility functions like isUndefined and isNull
const path = require('path');
const base64Img = require('base64-img');
const fs = require('fs');
const QRCode = require('qrcode');

exports.NotaCredito = async(data, cod_empresa, desc_empresa, ruta_logo) => {
  // CRÍTICO: Garante que 'ruta_logo' é uma string válida logo no início da função.
  // Isso nos ajudará a identificar se o problema é na entrada da função.
  if (typeof ruta_logo !== 'string' || ruta_logo.length === 0) {
    const errorMessage = `ERRO CRÍTICO: O parâmetro 'ruta_logo' em NotaCredito.js é inválido. Tipo: ${typeof ruta_logo}, Valor: ${ruta_logo}`;
    console.error(errorMessage);
    throw new Error(errorMessage);
  }

  let Body = [];
  // CORREÇÃO: Usar ruta_logo diretamente, pois já é o caminho absoluto passado da rota
  const archivo_logo = ruta_logo; 

  try { 
    // CORREÇÃO: Remover ._text para acessar os valores diretamente do objeto parsed
    let dNomEmi      = data.rDE?.DE?.gDatGralOpe?.gEmis?.dNomEmi || '';
    let dDesActEco = data.rDE?.DE?.gDatGralOpe?.gEmis?.gActEco?.[0]?.dDesActEco || ''; // gActEco pode ser um array
    let dEmailE = data.rDE?.DE?.gDatGralOpe?.gEmis?.dEmailE || ''; 
    let dTelEmi = data.rDE?.DE?.gDatGralOpe?.gEmis?.dTelEmi || '';
    let dDirEmi = data.rDE?.DE?.gDatGralOpe?.gEmis?.dDirEmi || '';
    let dDesDepEmi = data.rDE?.DE?.gDatGralOpe?.gEmis?.dDesDepEmi || '';
    let dDesDisEmi = data.rDE?.DE?.gDatGralOpe?.gEmis?.dDesDisEmi || ''; 
    
    // SEGUNDO QUADRO
    let dNumTim = data.rDE?.DE?.gTimb?.dNumTim || '';
    let dFeIniT = data.rDE?.DE?.gTimb?.dFeIniT || '';
    let dRucEm = data.rDE?.DE?.gDatGralOpe?.gEmis?.dRucEm || '';
    let dDVEmi = data.rDE?.DE?.gDatGralOpe?.gEmis?.dDVEmi || '';
    let dDesTiDE = data.rDE?.DE?.gTimb?.dDesTiDE || '';
    let dEst = data.rDE?.DE?.gTimb?.dEst || '';
    let dPunExp = data.rDE?.DE?.gTimb?.dPunExp || '';
    let dNumDoc = data.rDE?.DE?.gTimb?.dNumDoc || '';
    let dDesMotEmi = data.rDE?.DE?.gDtipDE?.gCamNCDE?.dDesMotEmi || '';
    let dEstDocAso = data.rDE?.DE?.gCamDEAsoc?.dEstDocAso || ''; 
    let dPExpDocAso = data.rDE?.DE?.gCamDEAsoc?.dPExpDocAso || '';
    let dNumDocAso = data.rDE?.DE?.gCamDEAsoc?.dNumDocAso || '';
    let iTipDocAso = data.rDE?.DE?.gCamDEAsoc?.iTipDocAso || '';
    let dCdCDERef = data.rDE?.DE?.gCamDEAsoc?.dCdCDERef || '';
    let dDesTipDocAso = data.rDE?.DE?.gCamDEAsoc?.dDesTipDocAso || '';
    let dFeEmiDE = moment(data.rDE?.DE?.gDatGralOpe?.dFeEmiDE || '').format('DD/MM/YYYY HH:mm:ss') ;

    // TERCER CUADRO
    let dNomRec = data.rDE?.DE?.gDatGralOpe?.gDatRec?.dNomRec || '';
    let dNomFanRec = data.rDE?.DE?.gDatGralOpe?.gDatRec?.dNomFanRec || '';
    let dDirRec = data.rDE?.DE?.gDatGralOpe?.gDatRec?.dDirRec || '';
    let dRucRec = data.rDE?.DE?.gDatGralOpe?.gDatRec?.dRucRec || '';
    let dDVRec = data.rDE?.DE?.gDatGralOpe?.gDatRec?.dDVRec || '';
    let dTelRec = data.rDE?.DE?.gDatGralOpe?.gDatRec?.dTelRec || '';
    let dDesCiuRec = data.rDE?.DE?.gDatGralOpe?.gDatRec?.dDesCiuRec || '';
    let dCodCliente = data.rDE?.DE?.gDatGralOpe?.gDatRec?.dCodCliente || '';

    let documento_asociado = dCdCDERef;
    if(iTipDocAso != '1') documento_asociado = `${dEstDocAso}-${dPExpDocAso}-${dNumDocAso}`
    
    let nombre_fantasia = `${dNomFanRec} ${dCodCliente}`
    if( dNomFanRec.length == 0 ) nombre_fantasia = ''

    let CodigoMoneda = data.rDE?.DE?.gDatGralOpe?.gOpeCom?.cMoneOpe || '';
    let Simbolo = 'Gs'
    let SeparadorDeMiles = '.';
    let SeparadorDeDecimales = ',';
    let CantidadDeDecimales = 0;
    let DescripcionMoneda = 'GUARANI ';
    if(CodigoMoneda == 'USD'){
      Simbolo = '$'
      SeparadorDeMiles = ',';
      SeparadorDeDecimales = '.';
      CantidadDeDecimales = 2;
      DescripcionMoneda = 'DOLAR US';
    }
    let Lines = data.rDE?.DE?.gDtipDE?.gCamItem;
    // CORREÇÃO: Acessar o atributo 'Id' diretamente do objeto DE
    var cdcprinc = data.rDE?.DE?.$?.Id || ''; 
    var cdc = cdcprinc.match(/.{1,4}/g)?.join(" ") || ''; // Adicionado ?. para segurança
    
    let dInfAdic = data.rDE?.gCamFuFD?.dInfAdic || null;
    let zona = '';
    let vendedor = '';
    let oc = '';
    if( dInfAdic !== null ){
      zona = dInfAdic.split('|')[0];
      vendedor = dInfAdic.split('|')[1];
      oc = dInfAdic.split('|')[2];
    }
    const dCarQR = data.rDE?.gCamFuFD?.dCarQR || '';
    let qr = await QRCode.toDataURL(dCarQR);
    Lines = _.isArray(Lines) ? Lines : [Lines]; 
    Lines.map( item => {
      Body = [ ...Body, {
        dGtin: item?.dGtin || '',
        dCantProSer: accounting.formatNumber(parseFloat(item?.dCantProSer || 0), 0, SeparadorDeMiles, SeparadorDeDecimales), 
        dDesUniMed: item?.dDesUniMed || '',
        dDesProSer: item?.dDesProSer || '',
        dCodInt: item?.dCodInt || '',
        dPUniProSer: accounting.formatNumber(parseFloat(item?.gValorItem?.dPUniProSer || 0), CantidadDeDecimales, SeparadorDeMiles, SeparadorDeDecimales),
        dDescItem: accounting.formatNumber( parseFloat( item?.gValorItem?.gValorRestaItem?.dDescItem || 0 ) * parseFloat(item?.dCantProSer || 0), CantidadDeDecimales, SeparadorDeMiles, SeparadorDeDecimales),
        
        gValorExenta: accounting.formatNumber(parseFloat(item?.gCamIVA?.dBasExe || 0), CantidadDeDecimales, SeparadorDeMiles, SeparadorDeDecimales),
        
        gValorIva5: accounting.formatNumber( parseFloat(item?.gCamIVA?.dTasaIVA || 0) === 5 ? (parseFloat(item?.gCamIVA?.dBasGravIVA || 0) + parseFloat(item?.gCamIVA?.dLiqIVAItem || 0)) : 0, CantidadDeDecimales, SeparadorDeMiles, SeparadorDeDecimales),
        gValorIva10: accounting.formatNumber( parseFloat(item?.gCamIVA?.dTasaIVA || 0) === 10 ? (parseFloat(item?.gCamIVA?.dBasGravIVA || 0) + parseFloat(item?.gCamIVA?.dLiqIVAItem || 0)) : 0, CantidadDeDecimales, SeparadorDeMiles, SeparadorDeDecimales),
        
        dInfItem: (item?.dInfItem && item.dInfItem.split('|')[0] == 'R') ? item.dInfItem.split('|')[1] : ' '  
      }]
    })
    let doc = new jsPDF('p','mm','a4', true);
    let totalPagesExp = "{total_pages_count_string}";
    let logo = '';
    try {
        if (fs.existsSync(archivo_logo)) {
            logo = base64Img.base64Sync(archivo_logo);
        } else {
            logo = '';
        }
    } catch (logoError) {
        console.error("Erro ao carregar logo da Nota de Crédito:", logoError);
        logo = '';
    }

    let columns = [
      { header: 'COD. BARRAS', dataKey: 'dGtin' },
      { header: 'CANT.', dataKey: 'dCantProSer' },
      { header: 'UNIDAD', dataKey: 'dDesUniMed' },
      { header: 'DESCRIPCION DEL PRODUCTO', dataKey: 'dDesProSer' },
      { header: 'CODIGO', dataKey: 'dCodInt' },
      { header: 'PRECIO UNITARIO', dataKey: 'dPUniProSer' },
      { header: 'DESCONTO', dataKey: 'dDescItem' },
      { header: 'EXENTA', dataKey: 'gValorExenta' },
      { header: '5%', dataKey: 'gValorIva5' },
      { header: '10%', dataKey: 'gValorIva10' },
    ];

    doc.autoTable({
      head: [columns.map(col => col.header)],
      body: Body.map(row => columns.map(col => row[col.dataKey])),
      theme: 'plain',
      showHead: false,
      bodyStyles: {
        overflow: 'linebreak',
        fontSize: 5,
        cellPadding: 1
      },
      margin: {
        top: 62,
        horizontal: 7,
        bottom: 60
      },
      columnStyles: {
        0: { cellWidth: 15, halign: 'left' },  // COD. BARRAS
        1: { cellWidth: 10, halign: 'right' }, // CANT.
        2: { cellWidth: 10, halign: 'center' },// UNIDAD
        3: { halign: 'left' },                 // DESCRIPCION DEL PRODUCTO (largura flexível)
        4: { cellWidth: 10, halign: 'center' },// CODIGO
        5: { cellWidth: 18, halign: 'right' }, // PRECIO UNITARIO
        6: { cellWidth: 15, halign: 'right' }, // DESCONTO
        7: { cellWidth: 15, halign: 'right' }, // EXENTA
        8: { cellWidth: 15, halign: 'right' }, // 5%
        9: { cellWidth: 15, halign: 'right' }, // 10%
      }, 
      didDrawPage: function (row, data) {
        doc.setDrawColor(0, 0, 0);
        doc.setLineWidth(0.2)
        // Primer Cuadro
        doc.roundedRect(7, 7, doc.internal.pageSize.getWidth() - 75, 30, 1, 1, 'S');
        // Logo - CORREÇÃO: Especifica o tipo 'PNG'
        if(logo && cod_empresa === '6') doc.addImage(logo, 'PNG', 10, 12, 37, 0, undefined,'FAST');
        if(logo && cod_empresa === '7') doc.addImage(logo, 'PNG', 10, 8, 30, 0, undefined,'FAST');
        if(cod_empresa === '4'){
          doc.setFontSize(12);
          doc.setFont(undefined, 'bold');
          doc.text(dNomEmi.toUpperCase(), 73, 12, 'center');
          doc.setFontSize(6);
          doc.text(dDesActEco, 73, 18, 'center'); 
          doc.setFont(undefined, 'normal');
          doc.text( 'Matriz: ' + dDirEmi.toUpperCase() , 73, 24, 'center'); 
          doc.text(`${dDesDisEmi} - ${dDesDepEmi}`, 73, 27, 'center');
          doc.text( 'Suc: ' + 'ESTANCIA SAN NICANOR - BAHIA NEGRA' , 73, 30, 'center'); 
          doc.text(`${dDesDisEmi} - ${dDesDepEmi}`, 73, 33, 'center');
          doc.text(`Teléfono: ${dTelEmi}`, 73, 36, 'center');
        }else{
          doc.setFontSize(12);
          doc.setFont(undefined, 'bold');
          doc.text(dNomEmi.toUpperCase(), 73, 12, 'center');
          doc.setFontSize(6);
          doc.text(dDesActEco, 73, 18, 'center'); 
          doc.setFont(undefined, 'normal');
          doc.text( dDirEmi.toUpperCase() , 73, 24, 'center'); 
          doc.setFont(undefined, 'normal');
          doc.text(`${dDesDisEmi} - ${dDesDepEmi}`, 73, 27, 'center');
          doc.text(`Teléfono: ${dTelEmi}`, 73, 30, 'center');
        }
        // Segundo Cuadro
        doc.roundedRect(143, 7, 60, 30, 1, 1, 'S');
        doc.setFontSize(7);
        doc.text(`TIMBRADO Nº ${dNumTim}`, 172, 12, 'center');
        doc.setFontSize(7);
        doc.text(`FECHA INICIO VIGENCIA ${ moment(dFeIniT).format('DD/MM/YYYY') }`, 172, 16, 'center');
        doc.setFontSize(7);
        doc.text(`RUC: ${dRucEm}-${dDVEmi}`, 172, 20, 'center');
        doc.setFontSize(12);
        doc.text(dDesTiDE, 172, 28, 'center');
        doc.setFontSize(12);
        doc.text(`${dEst}-${dPunExp}-${dNumDoc}`, 172, 34, 'center');
        // Cuarto Cuadro
        doc.roundedRect(7, 38, doc.internal.pageSize.getWidth() - 14, 15, 1, 1, 'S');
        // COLUMNA 1
        doc.setFontSize(5);
        doc.text('CLIENTE: ', 8, 41, 'left'); 
        doc.text(dNomRec, 20, 41, 'left');
        doc.setFontSize(5);
        doc.text('DIRECCION: ', 8, 44, 'left');
        doc.text(dDirRec, 20, 44, 'left');
        doc.setFontSize(5);
        doc.text('RUC/C.I.N: ', 8, 47, 'left');
        doc.text( `${dRucRec}-${dDVRec}`, 20, 47, 'left' );
        doc.setFontSize(5);
        doc.text('MOTIVO: ', 8, 50, 'left');
        doc.text(dDesMotEmi.toUpperCase(), 20, 50, 'left' ); 
        // COLUMNA 2
        doc.setFontSize(5);
        doc.text('FANTASIA: ', 85, 41, 'left');
        doc.setFontSize(5);
        doc.text(nombre_fantasia, 105, 41, 'left');
        doc.setFontSize(5);
        doc.text('CIUDAD: ', 85, 44, 'left');
        doc.text( `${dDesCiuRec}`, 115, 44, 'left');
        doc.setFontSize(5);
        doc.text('TIPO DOCUMENTO ASOCIADO: ', 85, 47, 'left');
        doc.text(dDesTipDocAso.toUpperCase(), 115, 47, 'left' ); 
        doc.setFontSize(5);
        doc.text('DOCUMENTO ASOCIADO: ', 85, 50, 'left'); 
        doc.text(documento_asociado, 115, 50, 'left' );
        // COLUMNA 3
        doc.setFontSize(5);
        doc.text('TELEFONO: ', 150, 41, 'left'); 
        doc.text(dTelRec, 170, 41, 'left');

        doc.setFontSize(5);
        doc.text('FECHA: ', 150, 44, 'left');
        doc.text(dFeEmiDE, 170, 44, 'left');  
        // Quinta Cuadro - Cabeçalhos da Tabela (AJUSTADO PARA NOVAS COLUNAS)
        doc.setDrawColor(0,0,0);
        doc.setFillColor(255,255,255);
        doc.roundedRect(6, 51, doc.internal.pageSize.getWidth() - 12, 10, 0, 0, 'F'); // Retângulo externo
        
        let currentX = 7;
        const headerY = 57;
        const headerYSub = 59; // Para sub-cabeçalhos
        const headerHeight = 10;
        const subHeaderHeight = 5;

        // COD. BARRAS
        doc.roundedRect(currentX, 51, 15, headerHeight, 0, 0, 'S');
        doc.text('COD. BARRAS', currentX + 7.5, headerY, 'center');
        currentX += 15;

        // CANT.
        doc.roundedRect(currentX, 51, 10, headerHeight, 0, 0, 'S');
        doc.text('CANT.', currentX + 5, headerY, 'center');
        currentX += 10;

        // UNIDAD
        doc.roundedRect(currentX, 51, 10, headerHeight, 0, 0, 'S');
        doc.text('UNIDAD', currentX + 5, headerY, 'center');
        currentX += 10;

        // DESCRIPCION DEL PRODUCTO (largura flexível, mas vamos dar uma base)
        const descWidth = (doc.internal.pageSize.getWidth() - 14) - (15 + 10 + 10 + 10 + 18 + 15 + 15 + 15 + 15); // Largura total - larguras fixas
        doc.roundedRect(currentX, 51, descWidth, headerHeight, 0, 0, 'S');
        doc.text('DESCRIPCION DEL PRODUCTO', currentX + (descWidth / 2), headerY, 'center');
        currentX += descWidth;

        // CODIGO
        doc.roundedRect(currentX, 51, 10, headerHeight, 0, 0, 'S');
        doc.text('CODIGO', currentX + 5, headerY, 'center');
        currentX += 10;

        // PRECIO UNITARIO
        doc.roundedRect(currentX, 51, 18, headerHeight, 0, 0, 'S');
        doc.text('PRECIO', currentX + 9, headerY - 1, 'center');
        doc.text('UNITARIO', currentX + 9, headerY + 2, 'center');
        currentX += 18;

        // DESCONTO
        doc.roundedRect(currentX, 51, 15, headerHeight, 0, 0, 'S');
        doc.text('DESCONTO', currentX + 7.5, headerY, 'center');
        currentX += 15;

        // VALOR DE VENTA (Cabeçalho principal)
        const valorVentaStart = currentX;
        const valorVentaWidth = 15 + 15 + 15; // Largura total das 3 sub-colunas
        doc.roundedRect(valorVentaStart, 51, valorVentaWidth, headerHeight, 0, 0, 'S');
        doc.text('VALOR DE VENTA', valorVentaStart + (valorVentaWidth / 2), 54, 'center');

        // Sub-colunas de VALOR DE VENTA
        // EXENTA
        doc.roundedRect(currentX, 51 + subHeaderHeight, 15, subHeaderHeight, 0, 0, 'S');
        doc.text('EXENTA', currentX + 7.5, headerYSub, 'center');
        currentX += 15;

        // 5%
        doc.roundedRect(currentX, 51 + subHeaderHeight, 15, subHeaderHeight, 0, 0, 'S');
        doc.text('5%', currentX + 7.5, headerYSub, 'center');
        currentX += 15;

        // 10%
        doc.roundedRect(currentX, 51 + subHeaderHeight, 15, subHeaderHeight, 0, 0, 'S');
        doc.text('10%', currentX + 7.5, headerYSub, 'center');
        currentX += 15;
      },
    });

    // AJUSTE DOS RETÂNGULOS PÓS-AUTOTABLE PARA AS NOVAS COLUNAS
    let finalY = doc.previousAutoTable.finalY;
    let startX = 7; // Início da primeira coluna

    // COD. BARRAS
    doc.roundedRect(startX, 51, 15, finalY - 51, 0, 0, 'S');
    startX += 15;

    // CANT.
    doc.roundedRect(startX, 51, 10, finalY - 51, 0, 0, 'S');
    startX += 10;

    // UNIDAD
    doc.roundedRect(startX, 51, 10, finalY - 51, 0, 0, 'S');
    startX += 10;

    // DESCRIPCION DEL PRODUCTO
    const descWidth = (doc.internal.pageSize.getWidth() - 14) - (15 + 10 + 10 + 10 + 18 + 15 + 15 + 15 + 15);
    doc.roundedRect(startX, 51, descWidth, finalY - 51, 0, 0, 'S');
    startX += descWidth;

    // CODIGO
    doc.roundedRect(startX, 51, 10, finalY - 51, 0, 0, 'S');
    startX += 10;

    // PRECIO UNITARIO
    doc.roundedRect(startX, 51, 18, finalY - 51, 0, 0, 'S');
    startX += 18;

    // DESCONTO
    doc.roundedRect(startX, 51, 15, finalY - 51, 0, 0, 'S');
    startX += 15;

    // VALOR DE VENTA (Sub-colunas)
    // EXENTA
    doc.roundedRect(startX, 51 + 5, 15, finalY - (51 + 5), 0, 0, 'S'); // Y ajustado para sub-cabeçalho
    startX += 15;

    // 5%
    doc.roundedRect(startX, 51 + 5, 15, finalY - (51 + 5), 0, 0, 'S');
    startX += 15;

    // 10%
    doc.roundedRect(startX, 51 + 5, 15, finalY - (51 + 5), 0, 0, 'S');
    startX += 15;


    doc.setFontSize(5);
    doc.rect(7, doc.previousAutoTable.finalY, doc.internal.pageSize.getWidth() - 14, 5, 'S'); 
    doc.rect(152, doc.previousAutoTable.finalY, 17, 5, 'S');
    doc.text(168, doc.previousAutoTable.finalY + 3, accounting.formatNumber(parseFloat(data.rDE?.DE?.gTotSub?.dSubExe || 0),CantidadDeDecimales,SeparadorDeMiles,SeparadorDeDecimales),'right');
    doc.rect(169, doc.previousAutoTable.finalY, 17, 5, 'S');
    doc.text(185, doc.previousAutoTable.finalY + 3, accounting.formatNumber(parseFloat(data.rDE?.DE?.gTotSub?.dSub5 || 0),CantidadDeDecimales,SeparadorDeMiles,SeparadorDeDecimales),'right');
    doc.rect(186, doc.previousAutoTable.finalY, 17, 5, 'S');
    doc.text(202, doc.previousAutoTable.finalY + 3, accounting.formatNumber(parseFloat(data.rDE?.DE?.gTotSub?.dSub10 || 0),CantidadDeDecimales,SeparadorDeMiles,SeparadorDeDecimales),'right');
    doc.setFontSize(5);
    doc.text('SUBTOTAL:', 8, doc.previousAutoTable.finalY + 3, 'left');
    doc.setFontSize(5);
    doc.text('LIQUIDACION DEL IVA:', 8, doc.previousAutoTable.finalY + 8, 'left');
    doc.setFontSize(5);
    doc.text('5 %: ', 40, doc.previousAutoTable.finalY + 8, 'left');
    doc.text( accounting.formatNumber(parseFloat(data.rDE?.DE?.gTotSub?.dIVA5 || 0), CantidadDeDecimales,SeparadorDeMiles,SeparadorDeDecimales) , 45, doc.previousAutoTable.finalY + 8, 'left');
    doc.setFontSize(5);
    doc.text('10 %: ', 70, doc.previousAutoTable.finalY + 8, 'left');
    doc.text( accounting.formatNumber(parseFloat(data.rDE?.DE?.gTotSub?.dIVA10 || 0), CantidadDeDecimales,SeparadorDeMiles,SeparadorDeDecimales) , 77, doc.previousAutoTable.finalY + 8, 'left');
    doc.setFontSize(5);
    doc.text('TOTAL: ', 100, doc.previousAutoTable.finalY + 8, 'left');
    doc.text( accounting.formatNumber(parseFloat(data.rDE?.DE?.gTotSub?.dTotIVA || 0),CantidadDeDecimales,SeparadorDeMiles,SeparadorDeDecimales) , 108, doc.previousAutoTable.finalY + 8, 'left');
    doc.setFillColor(255,255,255);
    doc.roundedRect(7, doc.previousAutoTable.finalY + 10, doc.internal.pageSize.getWidth() - 14, 6, 1, 1, 'F');
    doc.roundedRect(7, doc.previousAutoTable.finalY + 10, doc.internal.pageSize.getWidth() - 14, 6, 1, 1, 'S');
    doc.setFillColor(255,255,255);
    doc.rect(7.1, doc.previousAutoTable.finalY + 9.6, doc.internal.pageSize.getWidth() - 14.2, 1, 'F');
    doc.rect(7, doc.previousAutoTable.finalY + 5, doc.internal.pageSize.getWidth() - 14, 5.7, 'S');
    doc.setFontSize(5);
    doc.text('TOTAL A PAGAR (en letras):', 8, doc.previousAutoTable.finalY + 14, 'left'); 
    var TotalEnLetras = DescripcionMoneda + ' ' + num2word(parseFloat(data.rDE?.DE?.gTotSub?.dTotGralOpe || 0)) + ' =====';
    doc.text(33, doc.previousAutoTable.finalY + 14, TotalEnLetras);
    doc.text( 202, doc.previousAutoTable.finalY + 14, accounting.formatNumber(parseFloat(data.rDE?.DE?.gTotSub?.dTotGralOpe || 0),CantidadDeDecimales,SeparadorDeMiles,SeparadorDeDecimales),'right');
    doc.roundedRect(7, doc.previousAutoTable.finalY + 17, doc.internal.pageSize.getWidth() - 14, 27, 1, 1, 'S');
    doc.setFontSize(6);
    doc.addImage(qr,'JPG', 7.5, doc.previousAutoTable.finalY + 18, 0, 25, undefined,'FAST' );
    doc.text(33, doc.previousAutoTable.finalY + 21, 'Consulte a validade desta Fatura Eletrônica com o número de CDC impresso abaixo:');
    doc.text(33, doc.previousAutoTable.finalY + 24, 'https://ekuatia.set.gov.py/consultas/');
    doc.setFontSize(7);
    doc.setFont(undefined, 'bold');
    doc.text(33, doc.previousAutoTable.finalY + 29, 'CDC: ' + cdc);
    doc.setFontSize(5);
    doc.setFont(undefined, 'normal');
    doc.text(33, doc.previousAutoTable.finalY + 35, 'ESTE DOCUMENTO É UMA REPRESENTAÇÃO GRÁFICA DE UM DOCUMENTO ELETRÔNICO (XML)');
    doc.text(33, doc.previousAutoTable.finalY + 38, 'Informação de Interesse do faturador eletrônico emissor');
    doc.text(33, doc.previousAutoTable.finalY + 41, 'Se o seu documento eletrônico apresentar algum erro, poderá solicitar a modificação dentro das 72 horas seguintes da emissão deste comprovante.');
    // if (typeof doc.putTotalPages === 'function') doc.putTotalPages(totalPagesExp);
    
    // // CORREÇÃO: Saída do PDF como base64 e conversão para Buffer
    // const pdfBase64 = doc.output('base64');
    // return Buffer.from(pdfBase64, 'base64');

    if (typeof doc.putTotalPages === 'function') doc.putTotalPages(totalPagesExp);

    const pdfBuffer = doc.output('arraybuffer');
    return Buffer.from(pdfBuffer);    

  } catch (error) {
    console.error("Erro na geração do PDF da Nota de Crédito:", error); // Log de erro mais específico
    return { ret: 0, message: error.message || "Erro desconhecido na geração do PDF da Nota de Crédito." } // Retorna mensagem de erro mais detalhada
  }
}
