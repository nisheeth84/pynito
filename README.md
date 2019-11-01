# pynito
pynito is a Python package that will decrypt and validate AWS Cognito JWTs.

# Usage basics
pynito relies on a `CognitoDecryptor` class to store information about your cognito user pool needed to validate a given JWT. To initialize a `CognitoDecryptor`, you'll need to provide the endpoint of your cognito user pool (exported from your terraform cognito pool via `cognito_pool.endpoint`). If you're not sure what this is (if you're not using terraform), it can be constructed using your region and user pool id, by combining like so:
`cognito_endpoint = "cognito-idp." + COGNITO_AWS_REGION + ".amazonaws.com/" + COGNITO_USER_POOL_ID`. You should end up with something that looks like: `cognito_endpoint = 'cognito-idp.us-east-1.amazonaws.com/us-east-1_U9JdQXYne'`.

You'll also need to provide the app client ID, which will look something like `290cidr77bvsgi53d5shhftq4r`.
```python
from pynito import CognitoDecryptor
cognito = CognitoDecryptor(COGNITO_ENDPOINT, COGNITO_APP_CLIENT_ID)
```

Once you have the `CognitoDecryptor` object, you can call the `valid` function to validate JWTs. Valid takes in 2 arguments (and an optional 3rd). You must provide a string consisting of the JWT sent by cognito, and then you must also pass a string specifying the token claim type (either 'id' or 'access'). You may also optionally pass a boolean 3rd argument indicating if both token types (defaults to false).
```python
cognito_jwt = '<some cognito jwt>'

# only accept 'id' tokens
deciphered = cognito.valid(cognito_jwt, 'id')

# Either token type
deciphered2 = cognito.valid(cognito_jwt, 'id', True)
```
If the JWT is valid, a dictionary will be returned with the data encapsulated in the JWT. It might look something like this:
```python
{'sub': 'a9f5ca44-c25f-4a6d-8003-f95165ee6864', 'aud': '290cidr77bvsgi53d5shhftq4r', 'event_id': 'ff87d78c-a04a-4cd7-8b0a-3fd512e0d33e', 'token_use': 'id', 'auth_time': 1572635262, 'iss': 'https://cognito-idp.us-east-1.amazonaws.com/us-east-1_U9JdQXYne', 'phone_number_verified': True, 'cognito:username': 'a9f5ca44-c25f-4a6d-8003-f95165ee6864', 'phone_number': '+17828724212', 'exp': 1572638862, 'iat': 1572635262}
```
If the JWT is invalid, `None` will be returned. So an example use case might look like:
```python
from pynito import CognitoDecryptor
cognito = CognitoDecryptor(COGNITO_ENDPOINT, COGNITO_APP_CLIENT_ID)
cognito_jwt = '<some cognito jwt>'

deciphered = cognito.valid(cognito_jwt, 'id')

if deciphered:
    # Do something here now that you know this user is authenticated
    user_number = deciphered['phone_number']
```

# How does pynito verify a Cognito JWT?
Amazon lays out the process for verify a user pool token themselves [here](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html).

To verify a token pynito does the following steps in `valid()` (returning `None` if any stage fails) 
- Check that jwt is correctly formatted (contains a `kid` value in the header)
- Identify matching public kid from JWKs fetched from cognito pool (the JWTs `kid` **must** match a `kid` in the JWK set)
- Verify the JWT Signature
- Verify that the token hasn't expired
- Verify that the issuer matches the cognito endpoint
- Verify that the audience matches the app client id
- Verify that the token claim matches provided token claim (or if both token types allowed, matches either 'id' or 'access')

If all of these steps have completed without trouble, then `valid()` will return a dictionary comprised of the JWTs data. Otherwise it will return `None`.


