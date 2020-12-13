pyinstaller src/RailwaySim__main__.py -F `
--name "RailwaySim-windows" `
--icon='railwaysimicon.ico' `
--add-data "src\data\*;data" `
--add-data "src\data\*.jpg;data" `
--hidden-import <<name>> `
--clean