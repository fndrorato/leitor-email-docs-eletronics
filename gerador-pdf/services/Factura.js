const { jsPDF } = require('jspdf');
require('jspdf-autotable'); 

const accounting = require('accounting');
const moment = require('moment');
const num2word = require('../utils/num2word'); // Verifique o caminho e a existência
const path = require('path');
const base64Img = require('base64-img');
const fs = require('fs');
const QRCode = require('qrcode');

exports.Factura = async(data, cod_empresa, desc_empresa, ruta_logo) => {
  let Body = [];

  if (!ruta_logo || typeof ruta_logo !== 'string') {
    console.error("Erro: O parâmetro ruta_logo está vazio ou inválido.");
    throw new Error("O parâmetro ruta_logo está vazio ou inválido.");
  }

  const archivo_logo = ruta_logo;

  try { 
    let dNomEmi      = data.rDE?.DE?.gDatGralOpe?.gEmis?.dNomEmi || '';
    let dDesActEco   = data.rDE?.DE?.gDatGralOpe?.gEmis?.gActEco?.[0]?.dDesActEco || '';
    let dEmailE      = data.rDE?.DE?.gDatGralOpe?.gEmis?.dEmailE || '';
    let dTelEmi      = data.rDE?.DE?.gDatGralOpe?.gEmis?.dTelEmi || '';
    let dDirEmi      = data.rDE?.DE?.gDatGralOpe?.gEmis?.dDirEmi || '';
    let dDesDepEmi   = data.rDE?.DE?.gDatGralOpe?.gEmis?.dDesDepEmi || '';
    let dDesCiuEmi   = data.rDE?.DE?.gDatGralOpe?.gEmis?.dDesCiuEmi || '';
    
    let dNumTim      = data.rDE?.DE?.gTimb?.dNumTim || '';
    let dFeIniT      = data.rDE?.DE?.gTimb?.dFeIniT || '';
    let dRucEm       = data.rDE?.DE?.gDatGralOpe?.gEmis?.dRucEm || '';
    let dDVEmi       = data.rDE?.DE?.gDatGralOpe?.gEmis?.dDVEmi || '';
    let dFeEmiDE     = moment(data.rDE?.DE?.gDatGralOpe?.dFeEmiDE || '').format('DD/MM/YYYY HH:mm:ss') ;
    let dDesTiDE     = data.rDE?.DE?.gTimb?.dDesTiDE || '';
    let dEst         = data.rDE?.DE?.gTimb?.dEst || '';
    let dPunExp      = data.rDE?.DE?.gTimb?.dPunExp || '';
    let dNumDoc      = data.rDE?.DE?.gTimb?.dNumDoc || '';

    let iNatRec      = data.rDE?.DE?.gDatGralOpe?.gDatRec?.iNatRec || ''; 
    let dNomRec      = data.rDE?.DE?.gDatGralOpe?.gDatRec?.dNomRec || '';
    let dNomFanRec   = data.rDE?.DE?.gDatGralOpe?.gDatRec?.dNomFanRec || '';
    let dCodCliente  = data.rDE?.DE?.gDatGralOpe?.gDatRec?.dCodCliente || ''; 
    let dDirRec      = data.rDE?.DE?.gDatGralOpe?.gDatRec?.dDirRec || '';
    let dRucRec      = data.rDE?.DE?.gDatGralOpe?.gDatRec?.dRucRec || '';
    let dDVRec       = data.rDE?.DE?.gDatGralOpe?.gDatRec?.dDVRec || '';
    let dNumIDRec    = data.rDE?.DE?.gDatGralOpe?.gDatRec?.dNumIDRec || ''; 
    let dTelRec      = data.rDE?.DE?.gDatGralOpe?.gDatRec?.dTelRec || '';
    let dDesCiuRec   = data.rDE?.DE?.gDatGralOpe?.gDatRec?.dDesCiuRec || ''; 
    let dDesTipTra   = data.rDE?.DE?.gDatGralOpe?.gOpeCom?.dDesTipTra || '';

    let dIniTras     = data.rDE?.DE?.gDtipDE?.gTransp?.dIniTras ? moment(data.rDE.DE.gDtipDE.gTransp.dIniTras).format('DD/MM/YYYY') : '';
    let dFinTras     = data.rDE?.DE?.gDtipDE?.gTransp?.dFinTras ? moment(data.rDE.DE.gDtipDE.gTransp.dFinTras).format('DD/MM/YYYY') : '';
    let dMarVeh      = data.rDE?.DE?.gDtipDE?.gTransp?.gVehTras?.dMarVeh || '';
    let dNroMatVeh   = data.rDE?.DE?.gDtipDE?.gTransp?.gVehTras?.dNroMatVeh || '';
    let dNomTrans    = data.rDE?.DE?.gDtipDE?.gTransp?.gCamTrans?.dNomTrans || '';
    let dDirChof     = data.rDE?.DE?.gDtipDE?.gTransp?.gCamTrans?.dDirChof || '';
    let dNomChof     = data.rDE?.DE?.gDtipDE?.gTransp?.gCamTrans?.dNomChof || '';
    let dNumIDTrans  = data.rDE?.DE?.gDtipDE?.gTransp?.gCamTrans?.dNumIDTrans || '';
    let dNumIDChof   = data.rDE?.DE?.gDtipDE?.gTransp?.gCamTrans?.dNumIDChof || '';
    let dRucTrans    = data.rDE?.DE?.gDtipDE?.gTransp?.gCamTrans?.dRucTrans || '';
    let dDVTrans     = data.rDE?.DE?.gDtipDE?.gTransp?.gCamTrans?.dDVTrans || '';

    let iCondOpe = data.rDE?.DE?.gDtipDE?.gCamCond?.iCondOpe || '';
    let Contado = '';
    let Credito = '';
    if (iCondOpe === "1") {
      Contado = 'X';
    } else {
      Credito = 'X';
    }

    let plazo = data.rDE?.gCamFuFD?.dInfAdic?.split('|')[3] || '';
    if(iCondOpe === "2" ) plazo = data.rDE?.DE?.gDtipDE?.gCamCond?.gPagCred?.dPlazoCre || '';
    
    let numero_documento = `${dRucRec}-${dDVRec}`;
    if(iNatRec === '2') numero_documento = dNumIDRec;

    let CodigoMoneda = data.rDE?.DE?.gDatGralOpe?.gOpeCom?.cMoneOpe || '';
    let Simbolo = 'Gs'
    let SeparadorDeMiles = '.';
    let SeparadorDeDecimales = ',';
    let CantidadDeDecimales = 0;
    let Cantidadecimales = 0; 
    let DescripcionMoneda = 'GUARANI ';
    if(CodigoMoneda === 'USD'){
      Simbolo = '$'
      SeparadorDeMiles = '.';
      SeparadorDeDecimales = ',';
      CantidadDeDecimales = 2;
      Cantidadecimales = 2; 
      DescripcionMoneda = 'DOLAR US';
    }

    let Lines = data.rDE?.DE?.gDtipDE?.gCamItem;
    var cdcprinc = data.rDE?.DE?.$.Id || ''; 
    var cdc = cdcprinc.match(/.{1,4}/g)?.join(" ") || '';
    
    let dInfAdic = data.rDE?.gCamFuFD?.dInfAdic || null;
    let zona = '';
    let vendedor = '';
    let oc = '';
    if( dInfAdic !== null ){
      const infAdicParts = dInfAdic.split('|');
      zona = infAdicParts[0] || '';
      vendedor = infAdicParts[1] || '';
      oc = infAdicParts[2] || '';
    }
    const dCarQR = data.rDE?.gCamFuFD?.dCarQR || '';
    console.log('1. data existe?', !!data); // Transforma em booleano para checagem rápida

    // Checagem do Nível 1: rDE
    if (data && data.rDE) {
        console.log('2. data.rDE existe?', true, data.rDE);
        
        // Checagem do Nível 2: gCamFuFD
        if (data.rDE.gCamFuFD) {
            console.log('3. data.rDE.gCamFuFD existe?', true, data.rDE.gCamFuFD);
            
            // Checagem do Nível 3: dCarQR
            if (data.rDE.gCamFuFD.dCarQR) {
                console.log('4. data.rDE.gCamFuFD.dCarQR existe?', true, data.rDE.gCamFuFD.dCarQR);
                
                // Atribuição final (se for o caso)
                const dCarQR = data.rDE.gCamFuFD.dCarQR;
            } else {
                console.log('4. data.rDE.gCamFuFD.dCarQR não existe ou é falsy (null, undefined, etc.)');
            }
        } else {
            console.log('3. data.rDE.gCamFuFD não existe.');
        }
    } else {
        console.log('2. data.rDE não existe.');
    }    
    let qr = await QRCode.toDataURL(dCarQR);
    let columnBand = false;

    Lines = Array.isArray(Lines) ? Lines : (Lines ? [Lines] : []);

    Lines.map( item => {
      if(!columnBand) columnBand =  (item?.dInfItem && item.dInfItem.split('|')[0] === 'R') ? true : false;
      
      Body = [ ...Body, {
        dGtin: item?.dGtin || '',
        dCantProSer: accounting.formatNumber(parseFloat(item?.dCantProSer || 0),3, SeparadorDeMiles, SeparadorDeDecimales),
        dDesUniMed: item?.dDesUniMed || '',
        dDesProSer: item?.dDesProSer || '',
        dCodInt: item?.dCodInt || '',
        dPUniProSer: accounting.formatNumber(parseFloat(item?.gValorItem?.dPUniProSer || 0),4, SeparadorDeMiles, SeparadorDeDecimales),
        dDescItem: accounting.formatNumber( parseFloat( item?.gValorItem?.gValorRestaItem?.dDescItem || 0 ) * parseFloat(item?.dCantProSer || 0),CantidadDeDecimales, SeparadorDeMiles, SeparadorDeDecimales),
        
        gValorExenta: accounting.formatNumber( (item?.gCamIVA?.dPropIVA === '0' || !item?.gCamIVA?.dTasaIVA) ? parseFloat(item?.gValorItem?.dTotBruOpeItem || 0) : parseFloat(item?.gCamIVA?.dBasExe || 0), CantidadDeDecimales, SeparadorDeMiles, SeparadorDeDecimales),
        
        gValorIva5: accounting.formatNumber( item?.gCamIVA?.dTasaIVA === '5' ? (parseFloat(item?.gCamIVA?.dBasGravIVA || 0) + parseFloat(item?.gCamIVA?.dLiqIVAItem || 0)) : 0, CantidadDeDecimales, SeparadorDeMiles, SeparadorDeDecimales),
        gValorIva10: accounting.formatNumber( item?.gCamIVA?.dTasaIVA === '10' ? (parseFloat(item?.gCamIVA?.dBasGravIVA || 0) + parseFloat(item?.gCamIVA?.dLiqIVAItem || 0)) : 0, CantidadDeDecimales, SeparadorDeMiles, SeparadorDeDecimales),
        
        dInfItem: (item?.dInfItem && item.dInfItem.split('|')[0] === 'R') ? item.dInfItem.split('|')[1] : ' '
      }]
      if( item?.dInfItem ){
        if( item.dInfItem.split('|')[0] === 'D' ){
          Body = [ ...Body, {
            dDesProSer: item.dInfItem.split('|')[1],
          }]
        }
        if( item.dInfItem.split('|').length === 1 ){
          Body = [ ...Body, {
            dDesProSer: item.dInfItem,
          }]
        }
      }
    })

    let doc = new jsPDF('p','mm','a4');
    
    let totalPagesExp = "{total_pages_count_string}";
    let logo = '';
    try {
        if (fs.existsSync(archivo_logo)) {
            logo = base64Img.base64Sync(archivo_logo);
        } else {
            logo = '';
        }
    } catch (logoError) {
        console.error("Erro ao carregar logo:", logoError);
        logo = '';
    }

    let columns = [
      { header: 'COD. BARRAS', dataKey: 'dGtin' },
      { header: 'CANT.', dataKey: 'dCantProSer' },
      { header: 'UNIDAD', dataKey: 'dDesUniMed' },
      { header: 'DESCRIPCION DEL PRODUCTO', dataKey: 'dDesProSer' },
      { header: 'CODIGO', dataKey: 'dCodInt' },
      { header: 'PRECIO UNITARIO', dataKey: 'dPUniProSer' },
      { header: 'DESCUENTO', dataKey: 'dDescItem' },
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
        top: 61,
        horizontal: 7,
        bottom: 60
      },
      columnStyles: {
        0: { cellWidth: 15, halign: 'left' },
        1: { cellWidth: 10, halign: 'right' },
        2: { cellWidth: 10, halign: 'center' },
        3: { halign: 'left' },
        4: { cellWidth: 10, halign: 'center' },
        5: { cellWidth: 18, halign: 'right' },
        6: { cellWidth: 15, halign: 'right' },
        7: { cellWidth: 15, halign: 'right' },
        8: { cellWidth: 15, halign: 'right' },
        9: { cellWidth: 15, halign: 'right' },
      }, 
      didDrawPage: function (row, data) {
        doc.setDrawColor(0, 0, 0);
        doc.setLineWidth(0.2)
        // Primer Cuadro

        doc.roundedRect(7, 7, doc.internal.pageSize.getWidth() - 75, 30, 1, 1, 'S');
        // Logo - CORREÇÃO: Remove o tipo explícito, jsPDF inferirá do data URI
        if (logo && cod_empresa === '4') doc.addImage(logo, 'PNG', 10, 8, 35, 0, undefined, 'FAST');
        if (logo && cod_empresa === '5') doc.addImage(logo, 'PNG', 10, 12, 37, 0, undefined, 'FAST');
        if (logo && cod_empresa === '6') doc.addImage(logo, 'PNG', 10, 12, 37, 0, undefined, 'FAST');
        if (logo && cod_empresa === '7') doc.addImage(logo, 'PNG', 10, 8, 30, 0, undefined, 'FAST');

        if(cod_empresa === '4'){
          doc.setFontSize(12);
          doc.setFont(undefined, 'bold');
          doc.text(dNomEmi.toUpperCase(), 73, 12, 'center');
          doc.setFontSize(6);
          doc.text(dDesActEco, 73, 18, 'center');
          doc.setFont(undefined, 'normal');
          doc.text( 'Matriz: ' + dDirEmi.toUpperCase() , 73, 24, 'center'); 
          doc.text(`${dDesCiuEmi} - ${dDesDepEmi}`, 73, 27, 'center');
          doc.text( 'Suc: ' + 'ESTANCIA SAN NICANOR - BAHIA NEGRA' , 73, 30, 'center'); 
          doc.text(`${dDesCiuEmi} - ${dDesDepEmi}`, 73, 33, 'center');
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
          doc.text(`${dDesCiuEmi} - ${dDesDepEmi}`, 73, 27, 'center');
          doc.text(`Teléfono: ${dTelEmi}`, 73, 30, 'center');
        }
        
        // Segundo Cuadro
        doc.roundedRect(143, 7, 60, 20, 1, 1, 'S');
        doc.setFontSize(5);
        doc.text(`TIMBRADO Nº ${dNumTim}`, 172, 10, 'center');
        doc.setFontSize(4);
        doc.text(`FECHA INICIO VIGENCIA ${ moment(dFeIniT).format('DD/MM/YYYY') }`, 172, 12, 'center');
        doc.setFontSize(7);
        doc.text(`RUC: ${dRucEm}-${dDVEmi}`, 172, 16, 'center');
        doc.setFontSize(10);
        doc.text(dDesTiDE, 172, 21, 'center');
        doc.setFontSize(10);
        doc.text(`${dEst}-${dPunExp}-${dNumDoc}`, 172, 25, 'center');
        // tercer Cuadro
        doc.roundedRect(143, 28, 60, 9, 1, 1, 'S');
        doc.setFontSize(5);
        doc.text('COND. DE VENTA: ', 145, 33, 'left');
        doc.text('CONTADO', 180, 33, 'right');
        doc.text('CREDITO', 198, 33, 'right');
        doc.rect(166, 30, 4, 4, 'S');
        doc.rect(185, 30, 4, 4, 'S');
        doc.text(Contado, 168, 33, 'center');
        doc.text(Credito, 187, 33, 'center');
        // Cuarto Cuadro
        doc.roundedRect(7, 38, doc.internal.pageSize.getWidth() - 14, 14, 1, 1, 'S');
        // COLUMNA 1
        doc.setFontSize(5);
        doc.text('FECHA DE EMISION: ', 8, 41, 'left'); 
        doc.text(dFeEmiDE, 35, 41, 'left');
        doc.setFontSize(5);
        doc.text('NOMBRE O RAZON SOCIAL: ', 8, 44, 'left');
        doc.text(dNomRec, 35, 44, 'left');
        doc.setFontSize(5);
        doc.text('DIRECCION: ', 8, 47, 'left');
        doc.text(dDirRec.substring(0,100), 35, 47, 'left' );
        doc.setFontSize(5);
        // COLUMNA 3
        doc.setFontSize(5); 
        doc.text('TELEFONO: ', 140, 41, 'left');
        doc.text(dTelRec, 155, 41, 'left' );
        doc.setFontSize(5);
        doc.text('PLAZO: ', 140, 47, 'left');
        doc.text(plazo, 155, 47, 'left');
        doc.setFontSize(5);
        doc.text('RUC: ', 140, 44, 'left');
        doc.text(numero_documento, 155, 44, 'left');
        
        var str = "Página " + doc.internal.getNumberOfPages();
        if (typeof doc.putTotalPages === 'function') {
            str = str + " de " + totalPagesExp;
        }
        doc.setFontSize(5);
        doc.setTextColor(40);
        doc.text(str, doc.internal.pageSize.getWidth() + 12, 50, 'right');
        
        // Quinto Cuadro - Cabeçalhos da Tabela (AJUSTADO PARA NOVAS COLUNAS)
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

        // DESCUENTO
        doc.roundedRect(currentX, 51, 15, headerHeight, 0, 0, 'S');
        doc.text('DESCUENTO', currentX + 7.5, headerY, 'center');
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
    
    // Ajuste das posições para os totais do IVA
    // Subtotal Exentas
    doc.rect(7 + 15 + 10 + 10 + descWidth + 10 + 18 + 15, doc.previousAutoTable.finalY, 15, 5, 'S'); // Coluna Exentas
    doc.text(7 + 15 + 10 + 10 + descWidth + 10 + 18 + 15 + 15 - 1, doc.previousAutoTable.finalY + 3, accounting.formatNumber( parseFloat(data.rDE?.DE?.gTotSub?.dSubExe || 0) ,CantidadDeDecimales,SeparadorDeMiles,SeparadorDeDecimales),'right');
    
    // Subtotal 5%
    doc.rect(7 + 15 + 10 + 10 + descWidth + 10 + 18 + 15 + 15, doc.previousAutoTable.finalY, 15, 5, 'S'); // Coluna 5%
    doc.text(7 + 15 + 10 + 10 + descWidth + 10 + 18 + 15 + 15 + 15 - 1, doc.previousAutoTable.finalY + 3, accounting.formatNumber( parseFloat(data.rDE?.DE?.gTotSub?.dSub5 || 0) ,CantidadDeDecimales,SeparadorDeMiles,SeparadorDeDecimales),'right');
    
    // Subtotal 10%
    doc.rect(7 + 15 + 10 + 10 + descWidth + 10 + 18 + 15 + 15 + 15, doc.previousAutoTable.finalY, 15, 5, 'S'); // Coluna 10%
    doc.text(7 + 15 + 10 + 10 + descWidth + 10 + 18 + 15 + 15 + 15 + 15 - 1, doc.previousAutoTable.finalY + 3, accounting.formatNumber( parseFloat(data.rDE?.DE?.gTotSub?.dSub10 || 0) ,CantidadDeDecimales,SeparadorDeMiles,SeparadorDeDecimales),'right');
    
    doc.setFontSize(5);
    doc.text('SUBTOTAL:', 8, doc.previousAutoTable.finalY + 3, 'left');
    doc.rect(7, doc.previousAutoTable.finalY + 5, doc.internal.pageSize.getWidth() - 14, 5, 'S');
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
    doc.roundedRect(7, doc.previousAutoTable.finalY + 14, doc.internal.pageSize.getWidth() - 14, 10, 1, 1, 'S');
    doc.setFontSize(5);
    let text = `
      POR LA FALTA DE PAGO DE LA PRESENTE FACTURA Y/O DE OUTRA DEUDA PENDENTE ORIGINADA, EM QUALQUER CONCEPTO, AUTORIZO SUFICIENTEMENTE A LA FIRMA ${desc_empresa} UMA VEZ VENCIDO EL PLAZO, A INCLUIR, LAS OPERACOES PENDENTES EM MI NOMBRE Y/O RAZON SOCIAL AL QUE REPRESENTO, EN LA BASE DE DATOS DE INFORMCONF S.A PARA CONOCIMENTO DE TERCEROS INTERESSADOS DE LA CONFORMIDADE A LA LEY 1682
    `;
    var splitTitle = doc.splitTextToSize(text, doc.internal.pageSize.getWidth() - 17 );
    doc.text(8, doc.previousAutoTable.finalY + 16, splitTitle);
    doc.setFillColor(255,255,255);
    doc.rect(7, doc.previousAutoTable.finalY + 10, doc.internal.pageSize.getWidth() - 14, 5, 'F');
    doc.rect(7, doc.previousAutoTable.finalY + 10, doc.internal.pageSize.getWidth() - 14, 5, 'S');
    doc.rect(188, doc.previousAutoTable.finalY + 10, 15, 5, 'S');
    doc.setFontSize(5);
    doc.text('TOTAL A PAGAR (en letras):', 8, doc.previousAutoTable.finalY + 13, 'left'); 
    var TotalEnLetras = DescripcionMoneda + ' ' + num2word(parseFloat(data.rDE?.DE?.gTotSub?.dTotGralOpe || 0)) + ' =====';
    doc.text(33, doc.previousAutoTable.finalY + 13, TotalEnLetras);
    doc.text( 202, doc.previousAutoTable.finalY + 13, accounting.formatNumber(parseFloat(data.rDE?.DE?.gTotSub?.dTotGralOpe || 0), Cantidadecimales,SeparadorDeMiles,SeparadorDeDecimales),'right');
    doc.roundedRect(7, doc.previousAutoTable.finalY + 25, doc.internal.pageSize.getWidth() - 14, 27, 1, 1, 'S');
    doc.setFontSize(6);
    doc.addImage(qr,'JPG', 7.5, doc.previousAutoTable.finalY + 26, 0, 25, undefined,'FAST' );
    doc.text(33, doc.previousAutoTable.finalY + 28, 'Consulte a validade desta Fatura Eletrônica com o número de CDC impresso abaixo:');
    doc.text(33, doc.previousAutoTable.finalY + 31, 'https://ekuatia.set.gov.py/consultas/');
    doc.setFontSize(7);
    doc.setFont(undefined, 'bold');
    doc.text(33, doc.previousAutoTable.finalY + 37, 'CDC: ' + cdc);
    doc.setFontSize(5);
    doc.setFont(undefined, 'normal');
    doc.text(33, doc.previousAutoTable.finalY + 43, 'ESTE DOCUMENTO É UMA REPRESENTAÇÃO GRÁFICA DE UM DOCUMENTO ELETRÔNICO (XML)');
    doc.text(33, doc.previousAutoTable.finalY + 46, 'Informação de Interesse do faturador eletrônico emissor');
    doc.text(33, doc.previousAutoTable.finalY + 49, 'Se o seu documento eletrônico apresentar algum erro, poderá solicitar a modificação dentro das 72 horas seguintes da emissão deste comprovante.');

    if (typeof doc.putTotalPages === 'function') doc.putTotalPages(totalPagesExp);

    const pdfBuffer = doc.output('arraybuffer');
    return Buffer.from(pdfBuffer);


  } catch (error) {
    console.error("Erro na geração do PDF:", error);
    return { ret: 0, message: error.message || "Erro desconhecido na geração do PDF." }
  }
}
