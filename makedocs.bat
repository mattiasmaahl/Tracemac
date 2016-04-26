@echo off
cd docs
echo making new Doc-site...
call make html
if "%1" == "--with-pdf" (
	echo making new Latex
	call make latex
	echo converting to PDF
	call texify --clean --pdf build\latex\Tracemac.tex
)
echo all done!!
cd ..
