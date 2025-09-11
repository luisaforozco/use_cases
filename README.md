
In this repo I'm exploring if is possible to process a `database.csv` of Use cases and then create elements and connections in Miro, using the Miro Rest API.



## Connection with MIRO API

Define env variables with secrets, including `ACCESS_TOKEN`. This token expires and for that you will need to install the app in the browser (from settings page) and then you will be prompted to the `ACCESS_TOKEN`.
Export env variables:
```bash
source env.sh
```

Check that the connection works:
```python
import miro
miro.check_connection()
```


