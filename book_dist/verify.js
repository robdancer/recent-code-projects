const secretPassword = "password-goes-here";

function verifyCredentials(password) {
    return password === secretPassword;
}

exports.verifyCredentials = verifyCredentials;