import LegalDocumentLayout from '../components/LegalDocumentLayout';

function PrivacyPolicyPage() {
  return (
    <LegalDocumentLayout title="Privacy Policy">
      <p>
        This Privacy Policy describes how Talk to Folder (&quot;we&quot;,
        &quot;us&quot;) handles information when you connect Google Drive and
        index folders for chat.
      </p>

      <h2>Google Drive access</h2>
      <p>
        When you authorize the app, we request access only as needed to read the
        Google Drive folders you choose to add (for example, by providing a
        folder link). We use that access to retrieve file metadata and text
        content from supported files inside those folders so the product can
        work.
      </p>

      <h2>How folder content is used</h2>
      <p>
        Contents from your selected Drive folders are used to build context for
        the assistant and to generate responses to your questions. Your messages
        and retrieved context may be sent to third-party AI model providers as
        part of answering you. Those providers process data according to their
        own terms and policies.
      </p>

      <h2>Storage in our database</h2>
      <p>
        We store derived representations of your folder content in our databases
        (for example, text chunks and embeddings) so we can search and retrieve
        relevant context quickly for future messages in the same workspace. Chat
        messages and related application data may also be stored to operate the
        service.
      </p>
      <p>
        We do not use your Drive folder content to train our own models unless
        we tell you otherwise in writing. Third-party model providers may have
        their own rules about whether inputs are used for training; check their
        documentation if that matters for your use case.
      </p>

      <h2>Account and connection data</h2>
      <p>
        We may store identifiers needed to keep you signed in, link your account
        to Google, and associate indexed folders with your account.
      </p>

      <h2>Retention and deletion</h2>
      <p>
        We retain stored folder-derived data and chats for as long as needed to
        provide the service or as required by law. You can disconnect Google or
        stop using the service; contact us if you need specific data deleted and
        we will handle requests where we are reasonably able to do so.
      </p>

      <h2>Security</h2>
      <p>
        We use industry-standard measures appropriate to the nature of the
        service. No method of transmission or storage is completely secure.
      </p>

      <h2>Children</h2>
      <p>
        The service is not directed at children under 13, and we do not
        knowingly collect personal information from them.
      </p>

      <h2>Changes</h2>
      <p>
        We may update this policy from time to time. We will post the new
        version here and update the &quot;Last updated&quot; date.
      </p>

      <h2>Contact</h2>
      <p>
        For privacy questions, contact the team operating this deployment of
        Talk to Folder using the contact method they provide for the product.
      </p>
    </LegalDocumentLayout>
  );
}

export default PrivacyPolicyPage;
