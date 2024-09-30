import React, { useState, useEffect } from 'react';
import Web3 from 'web3';
import { create } from 'ipfs-http-client';
import DataVault from './contracts/DataVault.json';  // ABI JSON file

const ipfs = create({ host: 'ipfs.infura.io', port: 5001, protocol: 'https' });

function App() {
  const [account, setAccount] = useState('');
  const [contract, setContract] = useState(null);
  const [file, setFile] = useState(null);
  const [ipfsHash, setIpfsHash] = useState('');
  const [dataList, setDataList] = useState([]);

  useEffect(() => {
    loadBlockchainData();
  }, []);

  const loadBlockchainData = async () => {
    const web3 = new Web3(Web3.givenProvider || 'http://localhost:8545');
    const accounts = await web3.eth.requestAccounts();
    setAccount(accounts[0]);

    const networkId = await web3.eth.net.getId();
    const deployedNetwork = DataVault.networks[networkId];
    const contractInstance = new web3.eth.Contract(
      DataVault.abi,
      deployedNetwork && deployedNetwork.address
    );
    setContract(contractInstance);

    const userData = await contractInstance.methods.getUserData().call({ from: accounts[0] });
    setDataList(userData);
  };

  const handleFileUpload = async (event) => {
    setFile(event.target.files[0]);
  };

  const uploadToIPFS = async () => {
    if (file) {
      try {
        const added = await ipfs.add(file);
        const ipfsUri = `https://ipfs.infura.io/ipfs/${added.path}`;
        setIpfsHash(ipfsUri);
        alert(`File uploaded to IPFS: ${ipfsUri}`);
      } catch (err) {
        console.error('Error uploading to IPFS:', err);
      }
    } else {
      alert('Please select a file first.');
    }
  };

  const storeData = async () => {
    if (contract && ipfsHash) {
      try {
        await contract.methods.storeData(ipfsHash).send({ from: account });
        alert('Data stored successfully on the blockchain!');
        loadBlockchainData(); // Reload data
      } catch (err) {
        console.error('Error storing data on blockchain:', err);
      }
    } else {
      alert('Please upload file to IPFS first.');
    }
  };

  return (
    <div className="container">
      <h1>Decentralized Personal Data Vault</h1>
      <p>Connected Account: {account}</p>

      <div>
        <h2>Upload and Store Data</h2>
        <input type="file" onChange={handleFileUpload} />
        <button onClick={uploadToIPFS}>Upload to IPFS</button>
        <button onClick={storeData}>Store Data on Blockchain</button>
      </div>

      <div>
        <h2>Your Stored Data</h2>
        <ul>
          {dataList.map((dataId, index) => (
            <li key={index}>
              <p>Data ID: {dataId}</p>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default App;
