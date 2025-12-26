# 🎭 Rollar API - Frontend Integration

## 📡 API Response Format

### Authentication Response
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "phone": "+998901234567",
    "role": {
      "value": "user",
      "label": "User",
      "level": 1
    },
    "first_name": "Ali",
    "last_name": "Valiyev",
    "is_verified": true,
    "houses": [...]
  },
  "available_roles": [
    {
      "value": "super_admin",
      "label": "Super Admin",
      "level": 4
    },
    {
      "value": "government",
      "label": "Government Officer",
      "level": 3
    },
    {
      "value": "mahalla_admin",
      "label": "Neighborhood Admin",
      "level": 2
    },
    {
      "value": "user",
      "label": "User",
      "level": 1
    }
  ]
}
```

## 🔧 Frontend Implementation Examples

### React/Vue/Angular
```javascript
// 1. Login yoki SMS tasdiqlash
const response = await fetch('/api/users/auth/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    phone: '+998901234567',
    code: '123456',
    device_id: 'device_001',
    device_name: 'iPhone 13'
  })
});

const data = await response.json();

// 2. User rolini olish
const userRole = data.user.role;
console.log(userRole.value);  // "user"
console.log(userRole.label);  // "User"
console.log(userRole.level);  // 1

// 3. Role-based access control
if (userRole.level >= 3) {
  // Government yoki Super Admin
  console.log('High level access');
}

// 4. Role dropdown uchun barcha rollar
const roleOptions = data.available_roles;
/*
[
  { value: "super_admin", label: "Super Admin", level: 4 },
  { value: "government", label: "Government Officer", level: 3 },
  { value: "mahalla_admin", label: "Neighborhood Admin", level: 2 },
  { value: "user", label: "User", level: 1 }
]
*/
```

### React Component Example
```jsx
function UserProfile({ user }) {
  return (
    <div>
      <h2>{user.first_name} {user.last_name}</h2>
      <p>Phone: {user.phone}</p>
      <span className={`badge badge-${user.role.value}`}>
        {user.role.label}
      </span>
      {user.role.level >= 3 && (
        <button>Admin Panel</button>
      )}
    </div>
  );
}
```

### Vue Component Example
```vue
<template>
  <div>
    <h2>{{ user.first_name }} {{ user.last_name }}</h2>
    <span :class="'badge-' + user.role.value">
      {{ user.role.label }}
    </span>
    <button v-if="user.role.level >= 3">Admin Panel</button>
  </div>
</template>

<script>
export default {
  computed: {
    canEditUsers() {
      return this.user.role.level >= 2; // Mahalla admin va yuqori
    },
    isSuperAdmin() {
      return this.user.role.value === 'super_admin';
    }
  }
}
</script>
```

### Angular Component Example
```typescript
interface Role {
  value: string;
  label: string;
  level: number;
}

interface User {
  id: number;
  phone: string;
  role: Role;
  first_name: string;
  last_name: string;
  is_verified: boolean;
}

@Component({
  selector: 'app-user-profile',
  template: `
    <h2>{{ user.first_name }} {{ user.last_name }}</h2>
    <span [class]="'badge-' + user.role.value">
      {{ user.role.label }}
    </span>
    <button *ngIf="canManageUsers()">Manage Users</button>
  `
})
export class UserProfileComponent {
  @Input() user: User;

  canManageUsers(): boolean {
    return this.user.role.level >= 2;
  }

  isSuperAdmin(): boolean {
    return this.user.role.value === 'super_admin';
  }
}
```

## 🎨 Role-based UI Display

### CSS Styling
```css
/* Role badges */
.badge-super_admin {
  background: #dc3545; /* Red */
  color: white;
}

.badge-government {
  background: #007bff; /* Blue */
  color: white;
}

.badge-mahalla_admin {
  background: #28a745; /* Green */
  color: white;
}

.badge-user {
  background: #6c757d; /* Gray */
  color: white;
}
```

### Role Select Dropdown
```jsx
function RoleSelector({ availableRoles, currentRole, onChange }) {
  return (
    <select 
      value={currentRole.value} 
      onChange={(e) => onChange(e.target.value)}
    >
      {availableRoles.map(role => (
        <option key={role.value} value={role.value}>
          {role.label} (Level {role.level})
        </option>
      ))}
    </select>
  );
}
```

## 🔐 Access Control Patterns

### Permission Checker
```javascript
class PermissionChecker {
  constructor(userRole) {
    this.role = userRole;
  }

  canViewAllUsers() {
    return this.role.level >= 3; // Government+
  }

  canEditUsers() {
    return this.role.level >= 2; // Mahalla Admin+
  }

  canManageRegions() {
    return this.role.value === 'super_admin';
  }

  canScanQR() {
    return this.role.level >= 1; // All authenticated users
  }
}

// Usage
const permissions = new PermissionChecker(user.role);
if (permissions.canEditUsers()) {
  // Show edit button
}
```

## 📊 Role Hierarchy

| Level | Role Value       | Role Label           | Access                     |
|-------|------------------|----------------------|----------------------------|
| 4     | super_admin      | Super Admin          | Full system access         |
| 3     | government       | Government Officer   | View all data              |
| 2     | mahalla_admin    | Neighborhood Admin   | Manage neighborhood users  |
| 1     | user             | User                 | Own profile & QR scanning  |

## 🌐 API Endpoints

### GET User Profile
```http
GET /api/users/profile/
Authorization: Bearer {access_token}
```

Response:
```json
{
  "id": 1,
  "phone": "+998901234567",
  "role": {
    "value": "mahalla_admin",
    "label": "Neighborhood Admin",
    "level": 2
  },
  "first_name": "Ali",
  "last_name": "Valiyev",
  "is_verified": true
}
```

### UPDATE User Role (Admin only)
```http
PATCH /api/users/{id}/
Authorization: Bearer {admin_access_token}
Content-Type: application/json

{
  "role": "mahalla_admin"
}
```

## ✅ Best Practices

1. **Store role object in state/store**
```javascript
// Redux
const userSlice = createSlice({
  name: 'user',
  initialState: { role: null },
  reducers: {
    setUser: (state, action) => {
      state.role = action.payload.role;
    }
  }
});
```

2. **Create reusable role checkers**
```javascript
// utils/permissions.js
export const hasPermission = (userRole, requiredLevel) => {
  return userRole.level >= requiredLevel;
};

export const isRole = (userRole, roleName) => {
  return userRole.value === roleName;
};
```

3. **Protected routes**
```javascript
// React Router
function ProtectedRoute({ children, minLevel }) {
  const { user } = useAuth();
  
  if (user.role.level < minLevel) {
    return <Navigate to="/unauthorized" />;
  }
  
  return children;
}

// Usage
<Route path="/admin" element={
  <ProtectedRoute minLevel={3}>
    <AdminPanel />
  </ProtectedRoute>
} />
```
