// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract FileVault {
    struct FileEntry {
        address owner;
        string fileHash;
    }

    mapping(string => FileEntry) private files;

    event FileAdded(address indexed owner, string fileHash);

    function addFile(string memory fileHash) public {
        files[fileHash] = FileEntry({
            owner: msg.sender,
            fileHash: fileHash
        });
        emit FileAdded(msg.sender, fileHash);
    }

    function getFileOwner(string memory fileHash) public view returns (address) {
        return files[fileHash].owner;
    }

    function checkFileExists(string memory fileHash) public view returns (bool) {
        return files[fileHash].owner != address(0);
    }
}
