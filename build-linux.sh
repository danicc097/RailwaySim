pipenv run pyinstaller src/main.py \
--noconfirm \
--onefile \
--name "RailwaySim-linux" \
--paths="src/" \
--icon='src/mainicon.ico' \
--add-data "src/data/:data" \
--hidden-import RailwaySim \
--clean