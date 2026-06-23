import { jsPDF } from 'jspdf';
import autoTable from 'jspdf-autotable';

export function exportReportPdf({ title, kpis, tableHeaders, tableRows, filename }) {
  const doc = new jsPDF();
  doc.setFontSize(18);
  doc.text(title, 14, 20);
  doc.setFontSize(10);
  doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 28);

  let y = 36;
  if (kpis?.length) {
    doc.setFontSize(12);
    doc.text('Key Metrics', 14, y);
    y += 8;
    kpis.forEach(({ label, value }) => {
      doc.setFontSize(10);
      doc.text(`${label}: ${value}`, 14, y);
      y += 6;
    });
    y += 4;
  }

  if (tableHeaders?.length && tableRows?.length) {
    autoTable(doc, {
      startY: y,
      head: [tableHeaders],
      body: tableRows,
      styles: { fontSize: 8 },
      headStyles: { fillColor: [27, 79, 114] },
    });
  }

  doc.save(filename || 'report.pdf');
}
