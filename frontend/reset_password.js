import bcrypt from 'bcryptjs';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { MongoClient } from 'mongodb';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load environment variables
dotenv.config({ path: path.join(__dirname, '../.env') });

async function resetPassword() {
  const args = process.argv.slice(2);
  
  if (args.length < 2) {
    console.log('\n❌ Usage: node reset_password.js <email> <new-password>');
    console.log('\nExample: node reset_password.js user@example.com MyNewPassword123\n');
    process.exit(1);
  }

  const email = args[0];
  const newPassword = args[1];

  if (!process.env.MONGODB_ATLAS_URI) {
    console.error('❌ MONGODB_ATLAS_URI not found in environment variables');
    process.exit(1);
  }

  const client = new MongoClient(process.env.MONGODB_ATLAS_URI);

  try {
    console.log('🔌 Connecting to MongoDB...');
    await client.connect();
    console.log('✅ Connected to MongoDB');

    const db = client.db(process.env.MONGODB_DATABASE_NAME || 'textailor');
    const usersCollection = db.collection('users');

    // Find the user
    const user = await usersCollection.findOne({ email });
    
    if (!user) {
      console.error(`❌ User with email "${email}" not found`);
      process.exit(1);
    }

    console.log(`\n👤 Found user: ${email}`);
    console.log(`📅 Account created: ${user.createdAt}`);

    // Hash the new password
    console.log('\n🔒 Hashing new password...');
    const hashedPassword = await bcrypt.hash(newPassword, 12);

    // Update the password
    const result = await usersCollection.updateOne(
      { email },
      { 
        $set: { 
          password: hashedPassword,
          updatedAt: new Date()
        } 
      }
    );

    if (result.modifiedCount === 1) {
      console.log('✅ Password updated successfully!');
      console.log(`\n🎉 You can now log in with:`);
      console.log(`   Email: ${email}`);
      console.log(`   Password: ${newPassword}`);
    } else {
      console.error('❌ Failed to update password');
      process.exit(1);
    }

  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  } finally {
    await client.close();
    console.log('\n🔌 Disconnected from MongoDB\n');
  }
}

resetPassword();

