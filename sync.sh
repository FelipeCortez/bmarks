rsync -azP src/ felipecortez@felipecortez.net:/srv/www/marks;
ssh -t felipecortez.net "source /srv/www/marks/marksenv/bin/activate && python3 /srv/www/marks/manage.py collectstatic && sudo supervisorctl restart marks"
