> ## Documentation Index
> Fetch the complete documentation index at: https://docs.primeintellect.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Update User Limits

> Update any subset of the user's wallet usage limits.



## OpenAPI

````yaml https://api.primeintellect.ai/openapi.json patch /api/admin/users/{user_id}/usage-limits
openapi: 3.1.0
info:
  title: PI API
  version: 0.1.0
servers:
  - url: https://api.primeintellect.ai
security: []
paths:
  /api/admin/users/{user_id}/usage-limits:
    patch:
      tags:
        - admin-users
      summary: Update User Limits
      description: Update any subset of the user's wallet usage limits.
      operationId: update_user_limits_api_admin_users__user_id__usage_limits_patch
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
              $ref: '#/components/schemas/UpdateUsageLimitsRequest'
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/GenericResponse_WalletBillingInfo_'
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
    UpdateUsageLimitsRequest:
      properties:
        spendLimit:
          anyOf:
            - type: integer
            - type: 'null'
          title: Spendlimit
        overdraftLimit:
          anyOf:
            - type: integer
            - type: 'null'
          title: Overdraftlimit
        preventInstanceTermination:
          anyOf:
            - type: boolean
            - type: 'null'
          title: Preventinstancetermination
        instanceLimit:
          anyOf:
            - type: integer
            - type: 'null'
          title: Instancelimit
        sandboxTotalCpuLimit:
          anyOf:
            - type: integer
            - type: 'null'
          title: Sandboxtotalcpulimit
        sandboxTotalMemoryLimitGB:
          anyOf:
            - type: integer
            - type: 'null'
          title: Sandboxtotalmemorylimitgb
        sandboxTotalStorageLimitGB:
          anyOf:
            - type: integer
            - type: 'null'
          title: Sandboxtotalstoragelimitgb
        vmSandboxCreationBurstLimit:
          anyOf:
            - type: integer
              minimum: 0
            - type: 'null'
          title: Vmsandboxcreationburstlimit
        sharedDiskLimit:
          anyOf:
            - type: integer
            - type: 'null'
          title: Shareddisklimit
        sharedDiskTotalStorageGB:
          anyOf:
            - type: integer
            - type: 'null'
          title: Shareddisktotalstoragegb
        imageLimit:
          anyOf:
            - type: integer
            - type: 'null'
          title: Imagelimit
        imageTotalStorageGB:
          anyOf:
            - type: integer
            - type: 'null'
          title: Imagetotalstoragegb
        rftRunLimit:
          anyOf:
            - type: integer
            - type: 'null'
          title: Rftrunlimit
        rftTotalBatchLimit:
          anyOf:
            - type: integer
            - type: 'null'
          title: Rfttotalbatchlimit
        loraDeploymentLimit:
          anyOf:
            - type: integer
            - type: 'null'
          title: Loradeploymentlimit
        tunnelLimit:
          anyOf:
            - type: integer
            - type: 'null'
          title: Tunnellimit
        tunnelTtlHours:
          anyOf:
            - type: integer
            - type: 'null'
          title: Tunnelttlhours
        tunnelCreationsPerHourLimit:
          anyOf:
            - type: integer
            - type: 'null'
          title: Tunnelcreationsperhourlimit
        httpPortLimit:
          anyOf:
            - type: integer
            - type: 'null'
          title: Httpportlimit
        tcpPortLimit:
          anyOf:
            - type: integer
            - type: 'null'
          title: Tcpportlimit
        vmSandboxLimit:
          anyOf:
            - type: integer
            - type: 'null'
          title: Vmsandboxlimit
        vmSandboxGpuLimit:
          anyOf:
            - type: integer
            - type: 'null'
          title: Vmsandboxgpulimit
        tracesStorageLimitGB:
          anyOf:
            - type: integer
            - type: 'null'
          title: Tracesstoragelimitgb
      additionalProperties: false
      type: object
      title: UpdateUsageLimitsRequest
      description: |-
        Update any subset of a wallet's usage limits. Only provided fields are
        written (mirrors the platform ``changeWalletLimits``).
    GenericResponse_WalletBillingInfo_:
      properties:
        data:
          anyOf:
            - $ref: '#/components/schemas/WalletBillingInfo'
            - type: 'null'
          description: Response data
        status:
          anyOf:
            - type: string
            - type: 'null'
          title: Status
          description: Response status
      type: object
      title: GenericResponse[WalletBillingInfo]
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
    WalletBillingInfo:
      properties:
        walletId:
          type: string
          title: Walletid
        userId:
          anyOf:
            - type: string
            - type: 'null'
          title: Userid
        teamId:
          anyOf:
            - type: string
            - type: 'null'
          title: Teamid
        balance:
          type: integer
          title: Balance
        currency:
          type: string
          title: Currency
        autoTopUpActive:
          anyOf:
            - type: boolean
            - type: 'null'
          title: Autotopupactive
        monthlyInvoices:
          type: boolean
          title: Monthlyinvoices
          default: false
        limits:
          $ref: '#/components/schemas/UsageLimits'
      type: object
      required:
        - walletId
        - balance
        - currency
        - limits
      title: WalletBillingInfo
      description: >-
        Admin billing snapshot for a user/team wallet: balance, settings, and
        the

        configurable usage limits.
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
    UsageLimits:
      properties:
        spendLimit:
          type: integer
          title: Spendlimit
        overdraftLimit:
          type: integer
          title: Overdraftlimit
        preventInstanceTermination:
          type: boolean
          title: Preventinstancetermination
        instanceLimit:
          anyOf:
            - type: integer
            - type: 'null'
          title: Instancelimit
        sandboxTotalCpuLimit:
          type: integer
          title: Sandboxtotalcpulimit
        sandboxTotalMemoryLimitGB:
          type: integer
          title: Sandboxtotalmemorylimitgb
        sandboxTotalStorageLimitGB:
          type: integer
          title: Sandboxtotalstoragelimitgb
        vmSandboxCreationBurstLimit:
          type: integer
          title: Vmsandboxcreationburstlimit
        sharedDiskLimit:
          type: integer
          title: Shareddisklimit
        sharedDiskTotalStorageGB:
          type: integer
          title: Shareddisktotalstoragegb
        imageLimit:
          type: integer
          title: Imagelimit
        imageTotalStorageGB:
          type: integer
          title: Imagetotalstoragegb
        rftRunLimit:
          type: integer
          title: Rftrunlimit
        rftTotalBatchLimit:
          type: integer
          title: Rfttotalbatchlimit
        loraDeploymentLimit:
          type: integer
          title: Loradeploymentlimit
        tunnelLimit:
          type: integer
          title: Tunnellimit
        tunnelTtlHours:
          type: integer
          title: Tunnelttlhours
        tunnelCreationsPerHourLimit:
          type: integer
          title: Tunnelcreationsperhourlimit
        httpPortLimit:
          type: integer
          title: Httpportlimit
        tcpPortLimit:
          type: integer
          title: Tcpportlimit
        vmSandboxLimit:
          type: integer
          title: Vmsandboxlimit
        vmSandboxGpuLimit:
          type: integer
          title: Vmsandboxgpulimit
        tracesStorageLimitGB:
          type: integer
          title: Tracesstoragelimitgb
      type: object
      required:
        - spendLimit
        - overdraftLimit
        - preventInstanceTermination
        - sandboxTotalCpuLimit
        - sandboxTotalMemoryLimitGB
        - sandboxTotalStorageLimitGB
        - vmSandboxCreationBurstLimit
        - sharedDiskLimit
        - sharedDiskTotalStorageGB
        - imageLimit
        - imageTotalStorageGB
        - rftRunLimit
        - rftTotalBatchLimit
        - loraDeploymentLimit
        - tunnelLimit
        - tunnelTtlHours
        - tunnelCreationsPerHourLimit
        - httpPortLimit
        - tcpPortLimit
        - vmSandboxLimit
        - vmSandboxGpuLimit
        - tracesStorageLimitGB
      title: UsageLimits
      description: |-
        The configurable per-wallet resource/spend limits (the values an admin
        can view and update). Live usage counts are not included.
  securitySchemes:
    HTTPBearer:
      type: http
      scheme: bearer

````

This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.