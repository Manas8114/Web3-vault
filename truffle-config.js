const HDWalletProvider = require('@truffle/hdwallet-provider');
const Web3 = require('web3');
const infuraKey = "5a33b350d3e24f7a958225df0f6f9422"; // if you are using Infura

module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",     // Localhost (default: none)
      port: 8545,            // Standard Ethereum port (default: none)
      network_id: "*",       // Any network (default: none)
    },
    // other networks can be configured here
  },

};


