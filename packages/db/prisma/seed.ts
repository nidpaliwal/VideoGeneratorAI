import { PrismaClient, UserPlan, UserRole } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
  console.log('🌱 Seeding database...')

  // Create admin user
  const admin = await prisma.user.upsert({
    where: { email: 'admin@videogen.local' },
    update: {},
    create: {
      email: 'admin@videogen.local',
      name: 'Admin User',
      role: UserRole.ADMIN,
      plan: UserPlan.CREATOR,
      creditsRemaining: 9999,
      passwordHash: '$2b$10$dummyhashfordevonly', // password: admin123
    },
  })
  console.log('✅ Admin user created:', admin.email)

  // Create test user
  const testUser = await prisma.user.upsert({
    where: { email: 'test@videogen.local' },
    update: {},
    create: {
      email: 'test@videogen.local',
      name: 'Test User',
      role: UserRole.USER,
      plan: UserPlan.FREE,
      creditsRemaining: 3,
      passwordHash: '$2b$10$dummyhashfordevonly', // password: test123
    },
  })
  console.log('✅ Test user created:', testUser.email)

  // Create pro user
  const proUser = await prisma.user.upsert({
    where: { email: 'pro@videogen.local' },
    update: {},
    create: {
      email: 'pro@videogen.local',
      name: 'Pro User',
      role: UserRole.USER,
      plan: UserPlan.PRO,
      creditsRemaining: 50,
      passwordHash: '$2b$10$dummyhashfordevonly', // password: pro123
    },
  })
  console.log('✅ Pro user created:', proUser.email)

  console.log('🎉 Seeding completed!')
}

main()
  .catch((e) => {
    console.error('❌ Seeding failed:', e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })