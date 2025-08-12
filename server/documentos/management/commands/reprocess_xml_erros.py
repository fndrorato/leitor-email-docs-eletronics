# documentos/management/commands/reprocess_xml_erros.py
import os
import glob
import traceback
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# ajuste o import para onde sua função realmente está
from documentos.util import processar_nfe_xml  # EXEMPLO

class Command(BaseCommand):
    help = "Reprocessa XMLs com erro salvos em xmls_erros/"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dir", default="xmls_erros",
            help="Diretório onde estão os XMLs com erro (padrão: xmls_erros)"
        )
        parser.add_argument(
            "--pattern", default="*.xml",
            help="Glob pattern para selecionar arquivos (padrão: *.xml)"
        )
        parser.add_argument(
            "--limit", type=int, default=0,
            help="Limite de arquivos a processar (0 = todos)"
        )
        parser.add_argument(
            "--move-ok", action="store_true",
            help="Mover XMLs processados com sucesso para xmls_processados_ok/"
        )
        parser.add_argument(
            "--move-fail", action="store_true",
            help="Mover XMLs que falharem novamente para xmls_processados_fail/"
        )
        parser.add_argument(
            "--show-snippet", type=int, default=300,
            help="Tamanho do snippet de XML ao logar erro (padrão: 300)"
        )

    def handle(self, *args, **opts):
        base_dir = settings.BASE_DIR
        src_dir = os.path.join(base_dir, opts["dir"])
        pattern = os.path.join(src_dir, opts["pattern"])

        files = sorted(glob.glob(pattern))
        if not files:
            self.stdout.write(self.style.WARNING(f"Nenhum arquivo encontrado em {pattern}"))
            return

        limit = opts["limit"] or len(files)
        files = files[:limit]

        ok_dir = os.path.join(base_dir, "xmls_processados_ok")
        fail_dir = os.path.join(base_dir, "xmls_processados_fail")
        if opts["move_ok"]:
            os.makedirs(ok_dir, exist_ok=True)
        if opts["move_fail"]:
            os.makedirs(fail_dir, exist_ok=True)

        total = len(files)
        ok_count = 0
        fail_count = 0

        self.stdout.write(f"🔁 Reprocessando {total} arquivo(s) de {src_dir}…\n")

        for i, path in enumerate(files, 1):
            fname = os.path.basename(path)
            self.stdout.write(f"[{i}/{total}] 📄 {fname}")

            try:
                # tenta ler como UTF-8; se seus XMLs tiverem encoding variado,
                # podemos melhorar para detectar encoding depois
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    xml_content = f.read()

                # checa assinatura rápida (ajuste conforme sua regra)
                if "<DE Id=" not in xml_content:
                    self.stdout.write(self.style.WARNING(f"   ⏩ ignorado: não parece um DE válido."))
                    if opts["move_ok"]:
                        os.replace(path, os.path.join(ok_dir, fname))
                    ok_count += 1
                    continue

                doc, created = processar_nfe_xml(xml_content)

                if created:
                    self.stdout.write(self.style.SUCCESS(f"   ✅ Documento {getattr(doc, 'cdc', '(sem cdc)')} criado."))
                else:
                    self.stdout.write(self.style.NOTICE(f"   ⚠️ Documento {getattr(doc, 'cdc', '(sem cdc)')} já existia."))

                if opts["move_ok"]:
                    os.replace(path, os.path.join(ok_dir, fname))
                ok_count += 1

            except Exception as e:
                fail_count += 1
                self.stdout.write(self.style.ERROR(f"   ❌ Erro: {e}"))
                # trecho do XML para ajudar a debugar
                snippet_len = opts["show_snippet"]
                try:
                    snippet = xml_content[:snippet_len] if "xml_content" in locals() else "(sem conteúdo lido)"
                except Exception:
                    snippet = "(falha ao gerar snippet)"
                self.stdout.write(f"   📄 Snippet:\n{snippet}\n")
                self.stdout.write(self.style.WARNING("   🔎 Traceback:"))
                self.stdout.write(traceback.format_exc())

                if opts["move_fail"]:
                    try:
                        os.replace(path, os.path.join(fail_dir, fname))
                    except Exception as move_err:
                        self.stdout.write(self.style.WARNING(f"   ⚠️ Falha ao mover para fail: {move_err}"))

        self.stdout.write("\n📊 Resultado:")
        self.stdout.write(self.style.SUCCESS(f"   OK   : {ok_count}"))
        self.stdout.write(self.style.ERROR(  f"   FAIL : {fail_count}"))
        self.stdout.write(f"   TOTAL: {total}")
