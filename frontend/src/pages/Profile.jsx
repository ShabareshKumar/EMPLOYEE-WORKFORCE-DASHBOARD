import { useAuth } from '../context/AuthContext'

const Profile = () => {
  const { user } = useAuth()

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Profile</h1>

      <div className="card max-w-2xl">
        <div className="flex items-center gap-6 mb-8">
          <div className="w-24 h-24 bg-gradient-to-br from-pink-500 to-orange-500 rounded-full flex items-center justify-center text-4xl text-white font-bold">
            {user?.name?.charAt(0).toUpperCase()}
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{user?.name}</h2>
            <p className="text-gray-600 capitalize">{user?.role}</p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600 mb-1">Email</p>
            <p className="font-medium">{user?.email}</p>
          </div>

          <div className="p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600 mb-1">Department</p>
            <p className="font-medium">{user?.department || 'Not assigned'}</p>
          </div>

          <div className="p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600 mb-1">Role</p>
            <p className="font-medium capitalize">{user?.role}</p>
          </div>

          <div className="p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-600 mb-1">Member Since</p>
            <p className="font-medium">
              {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Profile
