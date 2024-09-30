import { create } from 'ipfs-http-client';

const ipfs = create('https://ipfs.infura.io:5001/api/v0'); // Infura's public IPFS node

const uploadFileToIPFS = async (file) => {
    try {
        const added = await ipfs.add(file);
        return `https://ipfs.infura.io/ipfs/${added.path}`; // Return the IPFS URL
    } catch (error) {
        console.error('Error uploading to IPFS', error);
    }
};
const ipfsUrl = `https://ipfs.infura.io/ipfs/${fileHash}`;
window.open(ipfsUrl); // Opens file in a new tab
