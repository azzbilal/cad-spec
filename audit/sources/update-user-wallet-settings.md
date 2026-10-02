> ## Documentation Index
> Fetch the complete documentation index at: https://docs.primeintellect.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Update User Wallet Settings

> Update auto top-up, its cap, and monthly invoicing.

Lowering the cap below the configured amount drags that amount down with it
and notifies the owner, since what gets billed to their card changes.
Turning auto top-up off also releases its in-progress lock.



## OpenAPI

````yaml https://api.primeintellect.ai/openapi.json patch /api/admin/users/{user_id}/wallet-settings
openapi: 3.1.0
info:
  title: PI API
  version: 0.1.0
servers:
  - url: https://api.primeintellect.ai
security: []
paths:
  /api/admin/users/{user_id}/wallet-settings:
    patch:
      tags:
        - admin-users
      summary: Update User Wallet Settings
      description: >-
        Update auto top-up, its cap, and monthly invoicing.


        Lowering the cap below the configured amount drags that amount down with
        it

        and notifies the owner, since what gets billed to their card changes.

        Turning auto top-up off also releases its in-progress lock.
      operationId: >-
        update_user_wallet_settings_api_admin_users__user_id__wallet_settings_patch
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
            title: User Id
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdateWalletSettingsRequest'
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/GenericResponse_WalletSettingsResult_'
        '401':
          description: Authorization failed
        '403':
          description: Insufficient permissions
        '422':
          description: Invalid request data
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
      security:
        - HTTPBearer: []
components:
  schemas:
    UpdateWalletSettingsRequest:
      properties:
        autoTopUpActive:
          anyOf:
            - type: boolean
            - type: 'null'
          title: Autotopupactive
        monthlyInvoices:
          anyOf:
            - type: boolean
            - type: 'null'
          title: Monthlyinvoices
        autoTopUpMaxValue:
          anyOf:
            - type: integer
              maximum: 9223372036854776000
              minimum: 100000
            - type: 'null'
          title: Autotopupmaxvalue
      additionalProperties: false
      type: object
      title: UpdateWalletSettingsRequest
      description: >-
        Admin edit of the wallet settings that are not usage limits.


        ``autoTopUpMaxValue`` distinguishes absent from explicit null: omitting
        it

        leaves the cap alone, passing null resets it to the platform default.
        The

        other two are tri-state for the same reason.
    GenericResponse_WalletSettingsResult_:
      properties:
        data:
          anyOf:
            - $ref: '#/components/schemas/WalletSettingsResult'
            - type: 'null'
          description: Response data
        status:
          anyOf:
            - type: string
            - type: 'null'
          title: Status
          description: Response status
      type: object
      title: GenericResponse[WalletSettingsResult]
    ErrorResponse:
      properties:
        errors:
          items:
            $ref: '#/components/schemas/ErrorDetail'
          type: array
          title: Errors
      type: object
      required:
        - errors
      title: ErrorResponse
    WalletSettingsResult:
      properties:
        walletId:
          type: string
          title: Walletid
        autoTopUpActive:
          anyOf:
            - type: boolean
            - type: 'null'
          title: Autotopupactive
        autoTopUpValue:
          anyOf:
            - type: integer
            - type: 'null'
          title: Autotopupvalue
        autoTopUpMaxValue:
          anyOf:
            - type: integer
            - type: 'null'
          title: Autotopupmaxvalue
        monthlyInvoices:
          type: boolean
          title: Monthlyinvoices
        clamped:
          type: boolean
          title: Clamped
          default: false
        notified:
          type: boolean
          title: Notified
          default: false
      type: object
      required:
        - walletId
        - monthlyInvoices
      title: WalletSettingsResult
    ErrorDetail:
      properties:
        param:
          type: string
          title: Param
        details:
          type: string
          title: Details
      type: object
      required:
        - param
        - details
      title: ErrorDetail
  securitySchemes:
    HTTPBearer:
      type: http
      scheme: bearer

````

This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.