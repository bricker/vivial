# async def normalize_services(services: list[OpenAIResponseService], model: _o.OpenAIModel) -> list[OpenAIResponseService]:
#     services_list = "\n".join([f"- {s['service_name']}: {s['service_description']}" for s in services])
#     print(services_list)

#     params = _o.ChatCompletionParameters(
#         messages=[
#             _o.ChatMessage(role=_o.ChatRole.SYSTEM, content=_o.formatprompt(
#                 f"""
#                 You will be provided with an ordered list of API service names and descriptions, which will be used for a system architecture diagram. Some items in the list refer to the same service but were given slightly different names and descriptions.

#                 Go through the list a few times and reduce it to a list of distinct services by removing services that are duplicates of a service earlier in the list. Two or more services are considered duplicates if their names and descriptions describe the same service, even if the names and descriptions don't perfectly match. When a duplicate is found, keep the one that is more detailed and discard the other one. You may combine the descriptions of the two services to get as much detail as possible, but do not change the name of any service. The names should be considered immutable.

#                 The provided list will be formatted like this:
#                 - <service_name>: <service_description>
#                 - <service_name>: <service_description>
#                 - <service_name>: <service_description>
#                 - ...

#                 {_OUTPUT_INSTRUCTIONS}
#                 """
#             )),
#             _o.formatprompt(
#                 f"""
#                 {services_list}
#                 """,
#             )
#         ],
#         model=model,
#         temperature=0,
#         # frequency_penalty: Optional[float] = None
#         # presence_penalty: Optional[float] = None
#         # temperature: Optional[float] = None
#     )

#     PROMPT_STORE["normalize_services"] = params

#     try:
#         response = await _o.chat_completion(params)
#         assert response
#         print(response)
#         reduced_services = parse_service_response(response)
#         return reduced_services
#     except MaxRetryAttemptsReachedError:
#         print("WARNING: Max retry attempts reached")
#         return services
