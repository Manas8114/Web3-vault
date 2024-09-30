// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DataVault {

    struct Data {
        string uri; // IPFS or decentralized storage URI
        address owner;
        bool shared;
        address[] sharedWith;
    }

    mapping(uint256 => Data) private vault;
    mapping(address => uint256[]) private userData; // User's owned data IDs
    uint256 private dataCounter;

    event DataStored(address indexed owner, uint256 dataId, string uri);
    event DataShared(uint256 dataId, address sharedWith);
    event DataAccessRevoked(uint256 dataId, address revokedFrom);

    modifier onlyOwner(uint256 _dataId) {
        require(vault[_dataId].owner == msg.sender, "Not the data owner");
        _;
    }

    // Store new data (URI to IPFS/Arweave)
    function storeData(string memory _uri) public returns (uint256) {
        dataCounter++;
        vault);
        userData[msg.sender].push(dataCounter);

        emit DataStored(msg.sender, dataCounter, _uri);
        return dataCounter;
    }

    // Share data with another user
    function shareData(uint256 _dataId, address _recipient) public onlyOwner(_dataId) {
        vault[_dataId].shared = true;
        vault[_dataId].sharedWith.push(_recipient);

        emit DataShared(_dataId, _recipient);
    }

    // Revoke access from a specific user
    function revokeAccess(uint256 _dataId, address _recipient) public onlyOwner(_dataId) {
        require(vault[_dataId].shared, "Data is not shared");

        for (uint256 i = 0; i < vault[_dataId].sharedWith.length; i++) {
            if (vault[_dataId].sharedWith[i] == _recipient) {
                delete vault[_dataId].sharedWith[i];
                emit DataAccessRevoked(_dataId, _recipient);
                break;
            }
        }
    }

    // Get user-owned data
    function getUserData() public view returns (uint256[] memory) {
        return userData[msg.sender];
    }

    // Get data by ID
    function getData(uint256 _dataId) public view returns (string memory, address, bool, address[] memory) {
        Data memory data = vault[_dataId];
        return (data.uri, data.owner, data.shared, data.sharedWith);
    }
}
