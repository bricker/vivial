


class GoogleOauthInit:
    @staticmethod
    async def handler() -> Response:
        oauth_flow_info = eave_core.internal.google_oauth.get_oauth_flow_info()
        response = RedirectResponse(url=oauth_flow_info.authorization_url)
        response.set_cookie(
            **shared_state_cookie_params(),
            value=oauth_flow_info.state,
        )
        return response


class GoogleOauthCallback:
    class RequestBody(BaseModel):
        state: Optional[str]
        code: Optional[str]
        error: Optional[str]

    @staticmethod
    async def handler(input: RequestBody, request: Request, response: Response) -> None:
        state = request.cookies.get("ev_oauth_state")
        assert state is not None

        credentials = eave_core.internal.google_oauth.get_oauth_credentials(uri=str(request.url), state=state)

        assert credentials.id_token is not None
        token = eave_core.internal.google_oauth.decode_id_token(id_token=credentials.id_token)
        userid = token.get("sub")
        assert userid is not None
        given_name = token.get("given_name")

        async with session_factory() as session:
            account_orm = await AccountOrm.find_one(session=session, auth_provider=AuthProvider.google, auth_id=userid)

            if account_orm is None:
                team = TeamOrm(
                    name=f"{given_name}'s Team" if given_name is not None else "Your Team",
                    document_platform=DocumentPlatform.unspecified,
                )

                session.add(team)
                await session.commit()

                account_orm = AccountOrm(
                    team_id=team.id,
                    auth_provider=AuthProvider.google,
                    auth_id=userid,
                    oauth_token=credentials.id_token,
                )

                session.add(account_orm)

            account_orm.oauth_token = credentials.id_token
            await session.commit()

        response = RedirectResponse(url=f"{APP_SETTINGS.eave_www_base}/setup")
        response.delete_cookie(**shared_state_cookie_params())

