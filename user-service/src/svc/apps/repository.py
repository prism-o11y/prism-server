from asyncpg.connection import Connection
import logging
from .models import Application
class AppRepository:

    def __init__(self, connection) -> None:
        self.connection:Connection = connection


    async def create_app(self, app:Application):

        async with self.connection.transaction():

            query = '''
                    INSERT INTO applications(app_id,org_id, app_name, app_url, created_at, updated_at)
                    VALUES($1,$2,$3,$4,$5,$6)
                    '''
            
            result = await self.connection.execute(
                query,
                app.app_id,
                app.org_id,
                app.app_name,
                app.app_url,
                app.created_at,
                app.updated_at,
            )

            row_updated = int(result.split(" ")[-1])
            if row_updated == 0:
                logging.error({"event": "Create-App", "app": app.app_name, "status": "Failed", "error": "Failed to create app"})
                return
            
        logging.info({"event": "Create-App", "app": app.app_name, "status": "Success"})
    