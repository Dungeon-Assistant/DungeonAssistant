from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

auth_key = '5-5_IKlbqznLoGN1GQvX1AYk0zNgWdzfmTQu4vgogl9h'
serv_url='https://api.us-south.assistant.watson.cloud.ibm.com/instances/02ca2e28-abb4-40c4-bb83-55fd22306435'
asst_id='6f4e748c-9409-48d6-a202-b2b8dc738351'

class Assistant():
    def __init__(self):
        self.authenticator = IAMAuthenticator(auth_key)
        self.assistant = AssistantV2(
            version = '2021-02-16',
            authenticator = self.authenticator
        )
        self.assistant.set_service_url(serv_url)

        self.createNewSession()

    def createNewSession(self):
        self.sesh_id = self.assistant.create_session(
            assistant_id=asst_id
        ).get_result()['session_id']

    def getResponse(self, message):
        response = self.assistant.message(
            assistant_id = asst_id,
            session_id = self.sesh_id,
            input={
                'message_type': 'text',
                'text': message,
            }
        ).get_result()

        return response['output']['generic']