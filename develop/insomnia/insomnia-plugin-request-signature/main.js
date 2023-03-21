const { signatureTemplateTag, signatureRequestHook } = require('./dist/main');

module.exports.templateTags = [signatureTemplateTag];
module.exports.requestHooks = [signatureRequestHook];
