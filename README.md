# Overview
This repository contains materials for a controlled demonstration using a Proxmark3/Easy setup to read NFC cards-specifically MiFare Ultralight-and program them for use with a new scanner. The demo was created for an internal training environment and is intended only for authorized, legitimate security research and access-control system education.

# Purpose of the Demo
The demo shows participants:
- How NFC card technologies differ  
- How tools like the Proxmark3 and Flipper Zero can read or emulate supported, properly authorized cards  
- How to recognize card types commonly encountered in access-control environments  

# Basic Demonstration (High-Level Summary)
The basic demo workflow involves:
- Launching the Proxmark3 client  
- Scanning an NFC card or tag to identify its technology  
- Interpreting the output  

This portion illustrates how different card types respond to standard scanning commands.

# Advanced Demonstration Summary
When a card is identified as MiFare Ultralight or MiFare Hospitality, the extended demo highlights:
- Collecting additional metadata  
- Verifying whether a card uses encryption  
- Emulating supported cards in a controlled lab environment  

**Note:** This demo must be performed only with cards you have explicit authorization to access. It is intended for educational forensics and security-awareness training, not for any production system.

# Troubleshooting (High-Level)
Common reasons for scan issues include:
1. The card is not NFC.  
2. The card is physically damaged.  
3. The card was moved before the scan completed.

# Card Types Explained

## MiFare DESFire
Modern, secure cards using AES-based encryption. When properly configured, they are robust and resistant to practical attacks.

## MiFare Classic
Widely deployed but uses legacy CRYPTO1 encryption, which was broken in 2008. These cards are considered insecure in modern environments.

## MiFare Ultralight
Low-cost cards with minimal or no encryption. Commonly used in disposable or low-risk applications.

## EM4100
Unencrypted plaintext RFID technology. Extremely easy to clone and unsuitable for secure access.

## HID Prox
Legacy technology relying primarily on security by obscurity rather than modern cryptography.

## Other Card Types
If an unfamiliar card is encountered, document its properties and consult the protocol information provided by Proxmark3 for additional analysis.

# Disclaimer
This project is for authorized research, education, and security training only. Do not attempt to scan, clone, emulate, or modify any access-control token without explicit permission from the owner or system administrator.

